import splink.comparison_library as cl
from pytest import raises
from splink import DuckDBAPI, Linker, SettingsCreator

import splinkclickhouse.comparison_library as cl_ch


def test_distance_in_km_level_at_thresholds(api_info, input_nodes_with_lat_longs):
    db_api = api_info["db_api"]

    settings = SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.ExactMatch("name"),
            cl_ch.DistanceInKMAtThresholds(
                "latitude",
                "longitude",
                [10, 50, 100, 200, 500],
            ),
        ],
    )

    linker = Linker(input_nodes_with_lat_longs, settings, db_api)
    linker.inference.predict()


def test_error_on_bad_calculation_method():
    with raises(ValueError):
        cl_ch.DistanceInKMAtThresholds(
            "latitude",
            "longitude",
            [10, 50, 100, 200, 500],
            calculation_method="invalid_method",
        )


def test_cant_use_distance_in_km_level_with_other_dialect(input_nodes_with_lat_longs):
    db_api = DuckDBAPI()

    settings = SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.ExactMatch("name"),
            cl_ch.DistanceInKMAtThresholds(
                "latitude",
                "longitude",
                [10, 50, 100, 200, 500],
            ),
        ],
    )

    with raises(ValueError):
        # this comparison level is not compatible with DuckDB (or other dialects)
        Linker(input_nodes_with_lat_longs, settings, db_api)

