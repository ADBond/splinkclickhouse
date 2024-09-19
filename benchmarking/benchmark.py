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

from splinkclickhouse import ChDBAPI, ClickhouseAPI

# settings for something fake_1000-shaped
blocking_rules = [
    block_on("first_name", "dob"),
    block_on("surname"),
]
settings = SettingsCreator(
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
    blocking_rules_to_generate_predictions=blocking_rules,
)


def timed_full_run(df: pd.DataFrame, backend_to_use: str) -> Timer:
    timer = Timer(backend_to_use)

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
        db_api = ClickhouseAPI(client)
    else:
        db_api = DuckDBAPI()

    db_api.delete_tables_created_by_splink_from_db()
    timer.append_time("data_ingested")

    cumulative_comparisons_to_be_scored_from_blocking_rules_chart(
        table_or_tables=df,
        blocking_rules=blocking_rules,
        db_api=db_api,
        link_type="dedupe_only",
    )
    timer.append_time("cumulative_comparisons_chart")

    linker = Linker(df, settings, db_api=db_api)
    timer.append_time("linker_instantiated")

    linker.training.estimate_probability_two_random_records_match(
        [block_on("first_name", "surname")],
        recall=0.7,
    )
    timer.append_time("estimate_probability_two_random_records_match")

    linker.training.estimate_u_using_random_sampling(max_pairs=1e8)
    timer.append_time("estimate_u")

    training_blocking_rule = block_on("first_name", "dob")
    linker.training.estimate_parameters_using_expectation_maximisation(
        training_blocking_rule, estimate_without_term_frequencies=True
    )
    timer.append_time("estimate_m_block_on_first_name_dob")
    training_blocking_rule = block_on("surname")
    linker.training.estimate_parameters_using_expectation_maximisation(
        training_blocking_rule, estimate_without_term_frequencies=True
    )
    timer.append_time("estimate_m_block_on_surname")

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

df = data_funcs[data_choice]()
# actually run things:
timer = timed_full_run(df, backend_to_use)

output_data_file = f"benchmarking/output/run_data_{data_choice}_{backend_to_use}.json"
with open(output_data_file, "w+") as f:
    json.dump(timer.records, f, indent=4)

multi_timer = MultiTimer([timer])
with pd.option_context("display.float_format", "{:,.3f}".format):
    print(multi_timer.timing_frame)  # noqa: T201
