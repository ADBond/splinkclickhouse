import splink.comparison_library as cl
from chdb import dbapi
from splink import Linker, SettingsCreator, block_on, splink_datasets

from splinkclickhouse import ChDBAPI

con = dbapi.connect()
db_api = ChDBAPI(con)

df = splink_datasets.fake_1000

settings = SettingsCreator(
    link_type="dedupe_only",
    comparisons=[
        cl.NameComparison("first_name"),
        cl.JaroAtThresholds("surname"),
        cl.DateOfBirthComparison(
            "dob",
            input_is_string=True,
        ),
        cl.DamerauLevenshteinAtThresholds("city").configure(
            term_frequency_adjustments=True
        ),
        cl.EmailComparison("email"),
    ],
    blocking_rules_to_generate_predictions=[
        block_on("first_name", "dob"),
        block_on("surname"),
    ],
)

linker = Linker(df, settings, db_api)

linker.training.estimate_probability_two_random_records_match(
    [block_on("first_name", "surname")],
    recall=0.7,
)
linker.training.estimate_u_using_random_sampling(max_pairs=1e6)
linker.training.estimate_parameters_using_expectation_maximisation(
    block_on("first_name", "surname")
)
linker.training.estimate_parameters_using_expectation_maximisation(block_on("email"))

pairwise_predictions = linker.inference.predict(threshold_match_weight=-5)

clusters = linker.clustering.cluster_pairwise_predictions_at_threshold(
    pairwise_predictions, 0.95
)

df_clusters = clusters.as_pandas_dataframe()
