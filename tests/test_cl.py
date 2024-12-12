import splink.comparison_library as cl
from pytest import mark
from splink import Linker, SettingsCreator

import splinkclickhouse.comparison_library as cl_ch


# TODO: for now there's not a straightforward way (afaik) to get an array column
# into chdb. So for the time being we test only clickhouse server version
@mark.clickhouse
@mark.clickhouse_no_core
def test_pairwise_string_distance(clickhouse_api_factory, input_nodes_with_name_arrays):
    db_api = clickhouse_api_factory()

    settings = SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.ExactMatch("username"),
            # can pretend these are distinct
            cl_ch.PairwiseStringDistanceFunctionAtThresholds(
                "aliases", "levenshtein", [1, 2]
            ),
            cl_ch.PairwiseStringDistanceFunctionAtThresholds(
                "aliases_2", "damerau_levenshtein", [1, 2, 3]
            ),
            cl_ch.PairwiseStringDistanceFunctionAtThresholds(
                "aliases_3", "jaro", [0.88, 0.7]
            ),
            cl_ch.PairwiseStringDistanceFunctionAtThresholds(
                "aliases_4", "jaro_winkler", [0.88, 0.7]
            ),
        ],
    )

    input_nodes_with_name_arrays["aliases_2"] = input_nodes_with_name_arrays["aliases"]
    input_nodes_with_name_arrays["aliases_3"] = input_nodes_with_name_arrays["aliases"]
    input_nodes_with_name_arrays["aliases_4"] = input_nodes_with_name_arrays["aliases"]
    linker = Linker(input_nodes_with_name_arrays, settings, db_api)
    linker.inference.predict()
