import clickhouse_connect
import splink.comparison_library as cl
from splink import Linker, SettingsCreator, block_on, splink_datasets

from splinkclickhouse import ClickhouseAPI

df = splink_datasets.fake_1000

tn = "fake_1000"
client = clickhouse_connect.get_client(
    host="localhost",
    port=8123,
    username="splinkognito",
    password="splink123!",
)
client.command(
    f"CREATE OR REPLACE TABLE {tn} "
    "(unique_id UInt32, first_name Nullable(String), surname Nullable(String), "
    "dob Nullable(String), city Nullable(String), email Nullable(String), "
    "cluster UInt8) "
    "ENGINE MergeTree "
    "ORDER BY unique_id"
)
client.insert_df(tn, df)

db_api = ClickhouseAPI(client)

# TODO: tf adjustments need deep work (can have _one_ but not more)
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
    blocking_rules_to_generate_predictions=[
        block_on("first_name", "dob"),
        block_on("surname"),
    ],
)

db_api.delete_tables_created_by_splink_from_db()

linker = Linker(tn, settings, db_api)

linker.training.estimate_probability_two_random_records_match(
    [block_on("first_name", "surname")],
    recall=0.7,
)
linker.training.estimate_u_using_random_sampling(max_pairs=1e5)
linker.training.estimate_parameters_using_expectation_maximisation(
    block_on("first_name", "surname")
)
linker.training.estimate_parameters_using_expectation_maximisation(block_on("email"))

pairwise_predictions = linker.inference.predict(threshold_match_weight=-5)

clusters = linker.clustering.cluster_pairwise_predictions_at_threshold(
    pairwise_predictions, 0.95
)

df_clusters = clusters.as_pandas_dataframe()
