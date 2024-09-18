from __future__ import annotations

from typing import Literal

from splink import ColumnExpression
from splink.internals.comparison_level_creator import ComparisonLevelCreator

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
        if sql_dialect is not ClickhouseDialect():
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
