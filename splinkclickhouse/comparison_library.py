from __future__ import annotations

from typing import Iterable, Literal

import splink.comparison_level_library as cll
from splink.internals.comparison_creator import ComparisonCreator
from splink.internals.comparison_level_creator import ComparisonLevelCreator
from splink.internals.misc import ensure_is_iterable

import splinkclickhouse.comparison_level_library as cll_ch


class DistanceInKMAtThresholds(ComparisonCreator):
    def __init__(
        self,
        lat_col: str,
        long_col: str,
        km_thresholds: Iterable[float] | float,
        calculation_method: Literal["great_circle", "wgs84"] = "wgs84",
    ):
        """
        A comparison of the latitude, longitude coordinates defined in
        'lat_col' and 'long col' giving the distance between them in km.

        An example of the output with km_thresholds = [1, 10] would be:

        - The two coordinates are within 1 km of one another
        - The two coordinates are within 10 km of one another
        - Anything else (i.e. the distance between coordinates are > 10km apart)

        This uses in-built Clickhouse functions to calculate the distance,
        either based on a spherical great-circle model, or based on WGS 84.

        Args:
            lat_col (str): The name of the latitude column to compare.
            long_col (str): The name of the longitude column to compare.
            km_thresholds (iterable[float] | float): The km threshold(s) for the
                distance levels.
            calculation_method (str): The method to use to compute distances from
                latitude and longitude.
                Can be 'great_circle' for the great circle distance, based on a
                spherical model (Clickhouse `greatCircleDistance`), or 'wgs84'
                to use the more accurate WGS 84 Ellipsoid model
                (Clickhouse `geoDistance`). Default 'wgs84'.
        """

        thresholds_as_iterable = ensure_is_iterable(km_thresholds)
        self.thresholds = [*thresholds_as_iterable]
        self.calculation_method = calculation_method
        super().__init__(
            col_name_or_names={
                "latitude_column": lat_col,
                "longitude_column": long_col,
            }
        )

    def create_comparison_levels(self) -> list[ComparisonLevelCreator]:
        lat_col = self.col_expressions["latitude_column"]
        long_col = self.col_expressions["longitude_column"]
        return [
            cll.Or(cll.NullLevel(lat_col), cll.NullLevel(long_col)),
            *[
                cll_ch.DistanceInKMLevel(
                    lat_col,
                    long_col,
                    km_threshold=threshold,
                    calculation_method=self.calculation_method,
                )
                for threshold in self.thresholds
            ],
            cll.ElseLevel(),
        ]

    def create_output_column_name(self) -> str:
        lat_col = self.col_expressions["latitude_column"]
        long_col = self.col_expressions["longitude_column"]
        return f"{lat_col.output_column_name}_{long_col.output_column_name}"

