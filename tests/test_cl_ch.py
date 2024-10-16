import splink.comparison_library as cl
from pytest import raises
from splink import DuckDBAPI, Linker, SettingsCreator

import splinkclickhouse.comparison_library as cl_ch


def test_distance_in_km_level_at_thresholds(api_info, input_nodes_with_lat_longs):
    db_api = api_info["db_api_factory"]()

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


def test_exact_match_substring_at_sizes(api_info, input_nodes_with_lat_longs):
    db_api = api_info["db_api_factory"]()

    settings = SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.ExactMatch("name"),
            cl_ch.ExactMatchAtSubstringSizes("geohashEncode(longitude, latitude)"),
        ],
    )

    linker = Linker(input_nodes_with_lat_longs, settings, db_api)
    linker.inference.predict()


def test_clickhouse_date_difference_at_thresholds(api_info, fake_1000):
    db_api = api_info["db_api_factory"]()

    settings = SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.ExactMatch("first_name"),
            cl_ch.AbsoluteDateDifferenceAtThresholds(
                "dob",
                input_is_string=True,
                metrics=["day", "day", "year", "year"],
                thresholds=[10, 30, 1, 5],
            ),
        ],
    )

    linker = Linker(fake_1000, settings, db_api)
    linker.inference.predict()
