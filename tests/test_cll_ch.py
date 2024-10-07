import splink.comparison_level_library as cll
import splink.comparison_library as cl
from pytest import raises
from splink import DuckDBAPI, Linker, SettingsCreator

import splinkclickhouse.comparison_level_library as cll_ch


def test_distance_in_km_level(api_info, input_nodes_with_lat_longs):
    db_api = api_info["db_api_factory"]()

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
