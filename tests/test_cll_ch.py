import splink.comparison_level_library as cll
import splink.comparison_library as cl
from pytest import mark, raises
from splink import DuckDBAPI, Linker, SettingsCreator, block_on

import splinkclickhouse.comparison_level_library as cll_ch
from splinkclickhouse.column_expression import ColumnExpression


@mark.parametrize("not_null", [True, False])
def test_distance_in_km_level(api_info, input_nodes_with_lat_longs, not_null):
    db_api = api_info["db_api_factory"]()

    null_level_list = (
        []
        if not_null
        else [cll.Or(cll.NullLevel("latitude"), cll.NullLevel("longitude"))]
    )

    settings = SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.ExactMatch("name"),
            cl.CustomComparison(
                comparison_levels=[
                    *null_level_list,
                    cll_ch.DistanceInKMLevel(
                        "latitude", "longitude", 10, not_null=not_null
                    ),
                    cll_ch.DistanceInKMLevel(
                        "latitude", "longitude", 50, not_null=not_null
                    ),
                    cll_ch.DistanceInKMLevel(
                        "latitude", "longitude", 100, not_null=not_null
                    ),
                    cll_ch.DistanceInKMLevel(
                        "latitude", "longitude", 200, not_null=not_null
                    ),
                    cll_ch.DistanceInKMLevel(
                        "latitude", "longitude", 500, not_null=not_null
                    ),
                    cll.ElseLevel(),
                ],
                output_column_name="latlong",
            ),
        ],
    )

    linker = Linker(input_nodes_with_lat_longs, settings, db_api)
    linker.inference.predict()


def test_error_on_bad_calculation_method():
    with raises(ValueError):
        cll_ch.DistanceInKMLevel("lat", "long", 5, calculation_method="invalid_method")


def test_cant_use_distance_in_km_level_with_other_dialect(input_nodes_with_lat_longs):
    db_api = DuckDBAPI()

    settings = SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.ExactMatch("name"),
            cl.CustomComparison(
                comparison_levels=[
                    cll.Or(cll.NullLevel("latitude"), cll.NullLevel("longitude")),
                    cll_ch.DistanceInKMLevel("latitude", "longitude", 10),
                    cll_ch.DistanceInKMLevel("latitude", "longitude", 50),
                    cll_ch.DistanceInKMLevel("latitude", "longitude", 100),
                    cll_ch.DistanceInKMLevel("latitude", "longitude", 200),
                    cll_ch.DistanceInKMLevel("latitude", "longitude", 500),
                    cll.ElseLevel(),
                ],
                output_column_name="latlong",
            ),
        ],
    )

    with raises(ValueError):
        # this comparison level is not compatible with DuckDB (or other dialects)
        Linker(input_nodes_with_lat_longs, settings, db_api)


@mark.parametrize(
    ("dob_column", "input_is_string"),
    [("dob", True), (ColumnExpression("dob").parse_date_to_int(), False)],
)
def test_custom_date_difference_level(api_info, fake_1000, dob_column, input_is_string):
    db_api = api_info["db_api_factory"]()

    settings = SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.ExactMatch("first_name"),
            cl.ExactMatch("surname"),
            cl.ExactMatch("email"),
            cl.CustomComparison(
                comparison_levels=[
                    cll.NullLevel(dob_column),
                    cll.ExactMatchLevel(dob_column),
                    cll_ch.AbsoluteDateDifferenceLevel(
                        dob_column,
                        input_is_string=input_is_string,
                        threshold=10,
                        metric="day",
                    ),
                    cll_ch.AbsoluteDateDifferenceLevel(
                        dob_column,
                        input_is_string=input_is_string,
                        threshold=30,
                        metric="day",
                    ),
                    cll_ch.AbsoluteDateDifferenceLevel(
                        dob_column,
                        input_is_string=input_is_string,
                        threshold=1,
                        metric="year",
                    ),
                    cll_ch.AbsoluteDateDifferenceLevel(
                        dob_column,
                        input_is_string=input_is_string,
                        threshold=5,
                        metric="year",
                    ),
                    cll.ElseLevel(),
                ],
                output_column_name="dob",
            ),
        ],
        blocking_rules_to_generate_predictions=[
            block_on("dob"),
            block_on("first_name", "surname"),
        ],
    )

    linker = Linker(fake_1000, settings, db_api)
    linker.inference.predict()
