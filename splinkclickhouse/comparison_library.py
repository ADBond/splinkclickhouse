from __future__ import annotations

from typing import Iterable, Literal

import splink.comparison_level_library as cll
from splink.internals.column_expression import ColumnExpression
from splink.internals.comparison_creator import ComparisonCreator
from splink.internals.comparison_level_creator import ComparisonLevelCreator
from splink.internals.comparison_library import (
    AbsoluteTimeDifferenceAtThresholds as SplinkAbsoluteTimeDifferenceAtThresholds,
)
from splink.internals.comparison_library import (
    DateMetricType,
    _DamerauLevenshteinIfSupportedElseLevenshteinLevel,
)
from splink.internals.comparison_library import (
    DateOfBirthComparison as SplinkDateOfBirthComparison,
)
from splink.internals.misc import ensure_is_iterable

import splinkclickhouse.comparison_level_library as cll_ch

from .column_expression import ColumnExpression as CHColumnExpression


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


class ExactMatchAtSubstringSizes(ComparisonCreator):
    def __init__(
        self,
        col_name: str,
        substring_size_or_sizes: Iterable[int] | int = [4, 3, 2],
        include_full_exact_match: bool = True,
    ):
        """
        A comparison between columns at several sizes of substring

        An example of the output with substring_size_or_sizes = [3, 1] and
        include_full_exact_match = True would be:

        - The two columns match exactly
        - The substring of the first three characters of each column match exactly
        - The substring of the first character of each column match exactly

        This is suitable for a hierarchically structured string, such as a geohash
        column (from e.g. the result of `geohashEncode`).
        See https://clickhouse.com/docs/en/sql-reference/functions/geo/geohash.

        Args:
            col_name (str): The name of the column to compare.
            long_col (str): The name of the longitude column to compare
            substring_size_or_sizes (iterable[int] | int): The size(s) of the substrings
                to compare, taken from the start of the string.
                Default [4, 3, 2]
            include_full_exact_match (bool): Whether or not to include a level for
                an exact match on the full string.
                Defaults to True.
        """

        sizes_as_iterable = ensure_is_iterable(substring_size_or_sizes)
        self.substring_sizes = [*sizes_as_iterable]
        self.include_full_exact_match = include_full_exact_match
        super().__init__(col_name)

    def create_comparison_levels(self) -> list[ComparisonLevelCreator]:
        raw_column = self.col_expression

        levels = [cll.NullLevel(raw_column)]
        if self.include_full_exact_match:
            levels.append(cll.ExactMatchLevel(raw_column))
        levels.extend(
            cll.ExactMatchLevel(raw_column.substr(1, threshold))
            for threshold in self.substring_sizes
        )
        levels.append(cll.ElseLevel())
        return levels

    def create_output_column_name(self) -> str:
        return self.col_expression.output_column_name


class AbsoluteDateDifferenceAtThresholds(SplinkAbsoluteTimeDifferenceAtThresholds):
    def __init__(
        self,
        col_name: str,
        *,
        input_is_string: bool,
        metrics: DateMetricType | list[DateMetricType],
        thresholds: float | list[float],
        term_frequency_adjustments: bool = False,
        invalid_dates_as_null: bool = True,
    ):
        super().__init__(
            col_name,
            input_is_string=input_is_string,
            metrics=metrics,
            thresholds=thresholds,
            datetime_format=None,
            term_frequency_adjustments=term_frequency_adjustments,
            invalid_dates_as_null=invalid_dates_as_null,
        )

    @property
    def datetime_parse_function(self):
        return lambda fmt: CHColumnExpression.from_base_expression(
            self.col_expression
        ).parse_date_to_int()

    @property
    def cll_class(self):
        return cll_ch.AbsoluteDateDifferenceLevel


class DateOfBirthComparison(SplinkDateOfBirthComparison):
    def __init__(
        self,
        col_name: str | ColumnExpression,
        *,
        input_is_string: bool,
        datetime_thresholds: float | Iterable[float] = (1, 1, 10),
        datetime_metrics: DateMetricType | Iterable[DateMetricType] = (
            "month",
            "year",
            "year",
        ),
        datetime_format: str = None,
        invalid_dates_as_null: bool = True,
    ):
        super().__init__(
            col_name=col_name,
            input_is_string=input_is_string,
            datetime_thresholds=datetime_thresholds,
            datetime_metrics=datetime_metrics,
            datetime_format=None,
        )

    @property
    def datetime_parse_function(self):
        return lambda fmt: CHColumnExpression.from_base_expression(
            self.col_expression
        ).parse_date_to_int()

    def create_comparison_levels(self) -> list[ComparisonLevelCreator]:
        # pretty much a copy of the Splink version, but unlike
        # AbsoluteDateDifferenceAtThresholds this does not allow a way
        # to hook in a different date-difference comparison level
        # so we duplicate, and just switch the date level
        if self.invalid_dates_as_null and self.input_is_string:
            null_col = self.datetime_parse_function(self.datetime_format)
        else:
            null_col = self.col_expression

        levels: list[ComparisonLevelCreator] = [
            cll.NullLevel(null_col),
        ]

        levels.append(
            cll.ExactMatchLevel(self.col_expression).configure(
                label_for_charts="Exact match on date of birth"
            )
        )

        if self.input_is_string:
            col_expr_as_string = self.col_expression
        else:
            col_expr_as_string = self.col_expression.cast_to_string()

        levels.append(
            _DamerauLevenshteinIfSupportedElseLevenshteinLevel(
                col_expr_as_string, distance_threshold=1
            ).configure(label_for_charts="DamerauLevenshtein distance <= 1")
        )

        if self.datetime_thresholds:
            for threshold, metric in zip(
                self.datetime_thresholds, self.datetime_metrics
            ):
                levels.append(
                    cll_ch.AbsoluteDateDifferenceLevel(
                        self.col_expression,
                        threshold=threshold,
                        metric=metric,
                        input_is_string=self.input_is_string,
                    ).configure(
                        label_for_charts=f"Abs date difference <= {threshold} {metric}"
                    )
                )

        levels.append(cll.ElseLevel())
        return levels
