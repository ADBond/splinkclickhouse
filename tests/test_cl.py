import splink.comparison_library as cl
from splink import Linker, SettingsCreator


def test_pairwise_string_distance(api_info, input_nodes_with_name_arrays):
    db_api = api_info["db_api_factory"]()

    settings = SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.ExactMatch("name"),
            # can pretend these are distinct
            cl.PairwiseStringDistanceFunctionAtThresholds(
                "aliases", "levenshtein", [1, 2]
            ),
            cl.PairwiseStringDistanceFunctionAtThresholds(
                "aliases", "damerau_levenshtein", [1, 2, 3]
            ),
            cl.PairwiseStringDistanceFunctionAtThresholds(
                "aliases", "jaro", [0.88, 0.7]
            ),
            cl.PairwiseStringDistanceFunctionAtThresholds(
                "aliases", "jaro_winkler", [0.88, 0.7]
            ),
        ],
    )

    linker = Linker(input_nodes_with_name_arrays, settings, db_api)
    linker.inference.predict()
