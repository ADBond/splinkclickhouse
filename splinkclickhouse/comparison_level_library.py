from __future__ import annotations

from typing import Literal

from splink import ColumnExpression
from splink.internals.comparison_level_creator import ComparisonLevelCreator
from splink.internals.comparison_level_library import (
    AbsoluteTimeDifferenceLevel as SplinkAbsoluteTimeDifferenceLevel,
)
from splink.internals.comparison_level_library import (
    DateMetricType,
)
from splink.internals.comparison_level_library import (
    PairwiseStringDistanceFunctionLevel as SplinkPairwiseStringDistanceFunctionLevel,
)

from .column_expression import ColumnExpression as CHColumnExpression
from .dialect import ClickhouseDialect, SplinkDialect


class DistanceInKMLevel(ComparisonLevelCreator):
    calculation_method_lookup = {
        "great_circle": "greatCircleDistance",
        "wgs84": "geoDistance",
    }

    def __init__(
        self,
        lat_col: str | ColumnExpression,
        long_col: str | ColumnExpression,
        km_threshold: float,
        not_null: bool = False,
        calculation_method: Literal["great_circle", "wgs84"] = "wgs84",
    ):
        """
        Compare the distance between two latitude and longitude coördinate points
        as measured in kilometres.

        Calculation uses in-built Clickhouse functions, which support either
        using great circle distance, or the slightly more accurate WGS 84 method.

        Arguments:
            lat_col (str): The name of a latitude column or the respective array
                or struct column column containing the information
                For example: long_lat['lat'] or long_lat[0]
            long_col (str): The name of a longitudinal column or the respective array
                or struct column column containing the information, plus an index.
                For example: long_lat['long'] or long_lat[1]
            km_threshold (int): The total distance in kilometers to evaluate your
                comparisons against
            not_null (bool): If true, ensure no attempt is made to compute this if
                any inputs are null. This is only necessary if you are not
                capturing nulls elsewhere in your comparison level.
            calculation_method (str): The method to use to compute distances from
                latitude and longitude.
                Can be 'great_circle' for the great circle distance, based on a
                spherical model (Clickhouse `greatCircleDistance`), or 'wgs84'
                to use the more accurate WGS 84 Ellipsoid model
                (Clickhouse `geoDistance`). Default 'wgs84'.

        """
        if calculation_method not in self.calculation_method_lookup:
            valid_opts_str = "', '".join(self.calculation_method_lookup.keys())
            raise ValueError(
                f"Calculation method must be one of {valid_opts_str}, "
                f"not '{calculation_method}'"
            )
        self.lat_col_expression = ColumnExpression.instantiate_if_str(lat_col)
        self.long_col_expression = ColumnExpression.instantiate_if_str(long_col)

        self.km_threshold = km_threshold
        self.not_null = not_null
        self.calculation_method = calculation_method

    def create_sql(self, sql_dialect: SplinkDialect) -> str:
        if not isinstance(sql_dialect, ClickhouseDialect):
            raise ValueError(
                "This version of `DistanceInKMLevel` is designed only for use "
                "with the Clickhouse dialect of SQL.\n"
                "Perhaps you meant to use "
                "`splink.comparison_level_library.DistanceInKMLevel`?"
            )
        self.lat_col_expression.sql_dialect = sql_dialect
        lat_col = self.lat_col_expression

        self.long_col_expression.sql_dialect = sql_dialect
        long_col = self.long_col_expression

        lat_l, lat_r = lat_col.name_l, lat_col.name_r
        long_l, long_r = long_col.name_l, long_col.name_r

        m_distance_function = self.calculation_method_lookup[self.calculation_method]

        # Clickhouse deals in metres
        m_threshold = self.km_threshold * 1000
        distance_km_sql = f"""
            {m_distance_function}({long_l}, {lat_l}, {long_r}, {lat_r}) <= {m_threshold}
        """.strip()

        if self.not_null:
            null_sql = " AND ".join(
                [f"{c} is not null" for c in [lat_r, lat_l, long_l, long_r]]
            )
            distance_km_sql = f"({null_sql}) AND {distance_km_sql}"

        return distance_km_sql

    def create_label_for_charts(self) -> str:
        return f"Distance less than {self.km_threshold}km"


class AbsoluteDateDifferenceLevel(SplinkAbsoluteTimeDifferenceLevel):
    def __init__(
        self,
        col_name: str | ColumnExpression,
        *,
        input_is_string: bool,
        threshold: float,
        metric: DateMetricType,
    ):
        """
        Computes the absolute time difference between two dates (total duration).
        For more details see Splink docs.

        In database this represents data as an integer counting number of days since
        1970-01-01 (Unix epoch).
        The input data can be either a string in YYYY-MM-DD format, or an
        integer of the number days since the epoch.

        Args:
            col_name (str): The name of the column to compare.
            input_is_string (bool): If True, the input dates are treated as strings
                and parsed to integers, and must be in ISO 8601 format.
            threshold (int): The maximum allowed difference between the two dates,
                in units specified by `date_metric`.
            metric (str): The unit of time to use when comparing the dates.
                Can be 'second', 'minute', 'hour', 'day', 'month', or 'year'.
        """
        super().__init__(
            col_name,
            input_is_string=input_is_string,
            threshold=threshold,
            metric=metric,
        )
        # need this to help mypy:
        self.col_expression: ColumnExpression

    @property
    def datetime_parsed_column_expression(self) -> CHColumnExpression:
        # convert existing ColumnExpression to our version,
        # and then apply parsing operation
        return CHColumnExpression.from_base_expression(
            self.col_expression
        ).parse_date_to_int()

    def create_sql(self, sql_dialect: SplinkDialect) -> str:
        self.col_expression.sql_dialect = sql_dialect
        if self.input_is_string:
            self.col_expression = self.datetime_parsed_column_expression

        col = self.col_expression

        # work in seconds as that's what parent uses, and we want to keep that machinery
        seconds_in_day = 86_400
        sql = (
            f"abs({col.name_l} - {col.name_r}) * {seconds_in_day} "
            f"<= {self.time_threshold_seconds}"
        )
        return sql


class PairwiseStringDistanceFunctionLevel(SplinkPairwiseStringDistanceFunctionLevel):
    def create_sql(self, sql_dialect: SplinkDialect) -> str:
        self.col_expression.sql_dialect = sql_dialect
        col = self.col_expression
        distance_function_name_transpiled = {
            "levenshtein": sql_dialect.levenshtein_function_name,
            "damerau_levenshtein": sql_dialect.damerau_levenshtein_function_name,
            "jaro_winkler": sql_dialect.jaro_winkler_function_name,
            "jaro": sql_dialect.jaro_function_name,
        }[self.distance_function_name]

        aggregator_func = {
            "min": sql_dialect.array_min_function_name,
            "max": sql_dialect.array_max_function_name,
        }[self._aggregator()]

        # order of the arguments is different in Clickhouse than tha expected by Splink
        # specifically the lambda must come first in Clickhouse
        # this is not fixable with UDF as having it in second argument in general
        # will cause Clickhouse parser to fail
        # also need to use a workaround to get 'flatten' equivalent for a single level
        return f"""{aggregator_func}(
                    {sql_dialect.array_transform_function_name}(
                        pair -> {distance_function_name_transpiled}(
                            pair[{sql_dialect.array_first_index}],
                            pair[{sql_dialect.array_first_index + 1}]
                        ),
                        arrayReduce(
                            'array_concat_agg',
                            {sql_dialect.array_transform_function_name}(
                                x -> {sql_dialect.array_transform_function_name}(
                                    y -> [x, y],
                                    {col.name_r}
                                ),
                                {col.name_l}
                            )
                        )
                    )
                ) {self._comparator()} {self.distance_threshold}"""
