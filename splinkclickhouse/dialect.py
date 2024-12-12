from splink.internals.comparison_level_library import (
    AbsoluteTimeDifferenceLevel,
    ArrayIntersectLevel,
)
from splink.internals.dialects import SplinkDialect


class ClickhouseDialect(SplinkDialect):
    _dialect_name_for_factory = "clickhouse"

    @property
    def sql_dialect_str(self) -> str:
        return "clickhouse"

    @property
    def levenshtein_function_name(self) -> str:
        return "editDistanceUTF8"

    @property
    def damerau_levenshtein_function_name(self) -> str:
        return "damerauLevenshteinDistance"

    @property
    def jaro_winkler_function_name(self) -> str:
        return "jaroWinklerSimilarity"

    @property
    def jaro_function_name(self) -> str:
        return "jaroSimilarity"

    @property
    def jaccard_function_name(self) -> str:
        return "stringJaccardIndexUTF8"

    @property
    def array_first_index(self) -> int:
        return 1

    @property
    def array_min_function_name(self) -> str:
        return "arrayMin"

    @property
    def array_max_function_name(self) -> str:
        return "arrayMax"

    @property
    def array_transform_function_name(self) -> str:
        return "arrayMap"

    def _regex_extract_raw(
        self, name: str, pattern: str, capture_group: int = 0
    ) -> str:
        return f"regexpExtract({name}, '{pattern}', {capture_group})"

    def try_parse_date(self, name: str, date_format: str = None) -> str:
        if date_format is not None:
            raise ValueError(
                "Clickhouse dialect does not support custom `date_format`. "
                "To use a custom format you must manually construct "
                "the relevant expression."
            )
        return f"""parseDateTime64BestEffortOrNull({name})"""

    def try_parse_timestamp(self, name: str, timestamp_format: str = None) -> str:
        if timestamp_format is not None:
            raise ValueError(
                "Clickhouse dialect does not support custom `date_format`. "
                "To use a custom format you must manually construct "
                "the relevant expression."
            )
        return f"""parseDateTime64BestEffortOrNull({name})"""

    def absolute_time_difference(self, clc: AbsoluteTimeDifferenceLevel) -> str:
        # need custom solution as sqlglot keeps TIME_TO_UNIX which is not available
        clc.col_expression.sql_dialect = self
        col = clc.col_expression

        return (
            f"ABS(AGE('second', {col.name_l}, {col.name_r}))"
            f"<= {clc.time_threshold_seconds}"
        )

    def array_intersect(self, clc: ArrayIntersectLevel) -> str:
        clc.col_expression.sql_dialect = self
        col = clc.col_expression
        threshold = clc.min_intersection
        return f"""
        length(arrayIntersect({col.name_l}, {col.name_r})) >= {threshold}
        """.strip()

    def random_sample_sql(
        self, proportion, sample_size, seed=None, table=None, unique_id=None
    ):
        if proportion == 1.0:
            return ""
        if seed:
            raise NotImplementedError(
                "Clickhouse sampling does not support a random seed. "
                "Please remove the `seed` parameter."
            )

        sample_size = int(sample_size)

        # SAMPLE n only works when we have specified the method in table creation
        return f"WHERE randCanonical() < {proportion}"

    @property
    def infinity_expression(self):
        return "Inf"
