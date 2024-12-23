import argparse
import json

import clickhouse_connect
import pandas as pd
import splink.comparison_library as cl
from chdb import dbapi
from splink import DuckDBAPI, Linker, SettingsCreator, block_on, splink_datasets
from splink.blocking_analysis import (
    cumulative_comparisons_to_be_scored_from_blocking_rules_chart,
)
from utils.timer import MultiTimer, Timer

from splinkclickhouse import ChDBAPI, ClickhouseServerAPI

# settings for something fake_1000-shaped
config_fake_1000 = {
    "settings": SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.JaroWinklerAtThresholds("first_name"),
            cl.JaroAtThresholds("surname"),
            cl.DateOfBirthComparison(
                "dob",
                input_is_string=True,
            ),
            cl.DamerauLevenshteinAtThresholds("city").configure(
                term_frequency_adjustments=True
            ),
            cl.JaccardAtThresholds("email"),
        ],
        blocking_rules_to_generate_predictions=[
            block_on("first_name", "dob"),
            block_on("surname"),
        ],
    ),
    "deterministic_rules": [block_on("first_name", "surname")],
    "em_cols": [
        ("first_name", "surname"),
        ("email",),
    ],
}
config_historical_50k = {
    "settings": SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            # cl.ForenameSurnameComparison(
            #     "first_name",
            #     "surname",
            #     forename_surname_concat_col_name="first_and_surname",
            # ),
            cl.DamerauLevenshteinAtThresholds("first_name"),
            cl.DamerauLevenshteinAtThresholds("surname"),
            # cl.DateOfBirthComparison("dob", input_is_string=True),
            cl.ExactMatch("dob"),
            cl.LevenshteinAtThresholds("postcode_fake"),
            cl.ExactMatch("birth_place"),
            cl.ExactMatch("occupation"),
        ],
        blocking_rules_to_generate_predictions=[
            block_on("substr(first_name,1,3)", "substr(surname,1,4)"),
            block_on("surname", "dob"),
            block_on("first_name", "dob"),
            block_on("postcode_fake", "first_name"),
            block_on("postcode_fake", "surname"),
            block_on("dob", "birth_place"),
            block_on("substr(postcode_fake,1,3)", "dob"),
            block_on("substr(postcode_fake,1,3)", "first_name"),
            block_on("substr(postcode_fake,1,3)", "surname"),
            block_on(
                "substr(first_name,1,2)", "substr(surname,1,2)", "substr(dob,1,4)"
            ),
        ],
    ),
    "deterministic_rules": [
        block_on("first_name", "surname", "dob"),
        block_on("substr(first_name, 1, 2)", "surname", "substr(postcode_fake, 1, 2)"),
        block_on("dob", "postcode_fake"),
    ],
    "em_cols": [
        ("first_name", "surname"),
        ("dob",),
    ],
}


def timed_full_run(data: str, config: dict, backend_to_use: str) -> Timer:
    timer = Timer(backend_to_use, data)

    df = data_funcs[data_choice]()

    timer.append_time("start")

    if backend_to_use == "chdb":
        con = dbapi.connect()
        db_api = ChDBAPI(con)
    elif backend_to_use == "clickhouse":
        client = clickhouse_connect.get_client(
            host="localhost",
            port=8123,
            username="splinkognito",
            password="splink123!",
        )
        db_api = ClickhouseServerAPI(client)
    elif backend_to_use == "duckdb":
        db_api = DuckDBAPI()
    else:
        raise ValueError(f"Unknown backend: {backend_to_use}")

    db_api.delete_tables_created_by_splink_from_db()
    timer.append_time("data_ingested")

    settings = config["settings"]
    cumulative_comparisons_to_be_scored_from_blocking_rules_chart(
        table_or_tables=df,
        blocking_rules=settings.blocking_rules_to_generate_predictions,
        db_api=db_api,
        link_type="dedupe_only",
    )
    timer.append_time("cumulative_comparisons_chart")

    linker = Linker(df, settings, db_api=db_api)
    timer.append_time("linker_instantiated")

    linker.training.estimate_probability_two_random_records_match(
        config["deterministic_rules"],
        recall=0.7,
    )
    timer.append_time("estimate_probability_two_random_records_match")

    linker.training.estimate_u_using_random_sampling(max_pairs=1e7)
    timer.append_time("estimate_u")

    for cols in config["em_cols"]:
        training_blocking_rule = block_on(*cols)
        linker.training.estimate_parameters_using_expectation_maximisation(
            training_blocking_rule, estimate_without_term_frequencies=True
        )
        timer.append_time(f"estimate_m_block_on_{'_'.join(cols)}")

    df_predict = linker.inference.predict()
    timer.append_time("predict")

    linker.clustering.cluster_pairwise_predictions_at_threshold(df_predict, 0.9)
    timer.append_time("cluster_at_90")

    timer.summarise_times()
    return timer


# make them functions so we don't download if we don't need
data_funcs = {
    "fake_1000": lambda: splink_datasets.fake_1000,
    "fake_20000": lambda: pd.read_csv(
        "https://raw.githubusercontent.com/moj-analytical-services/splink_demos/refs/heads/master/data/fake_20000.csv"
    ),
    "historical_50k": lambda: splink_datasets.historical_50k,
}
configs = {
    "fake_1000": config_fake_1000,
    "fake_20000": config_fake_1000,
    "historical_50k": config_historical_50k,
}

parser = argparse.ArgumentParser(prog="Benchmarker", description="Rough benchmarking")
parser.add_argument(
    "data_choice",
    help="See `data_funcs` for options",
)
parser.add_argument(
    "backend_to_use",
    help="Can be 'duckdb', 'clickhouse', or 'chdb'",
)
args = parser.parse_args()

data_choice = args.data_choice
backend_to_use = args.backend_to_use

config = configs[data_choice]
# actually run things:
timer = timed_full_run(data_choice, config, backend_to_use)

output_data_file = f"benchmarking/output/run_data_{data_choice}_{backend_to_use}.json"
print(f"Writing data to to {output_data_file}")  # noqa: T201
with open(output_data_file, "w+") as f:
    json.dump(timer.records, f, indent=4)

multi_timer = MultiTimer([timer])
with pd.option_context("display.float_format", "{:,.3f}".format):
    print(multi_timer.timing_frame)  # noqa: T201
