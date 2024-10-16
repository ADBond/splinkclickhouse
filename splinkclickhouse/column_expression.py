from copy import copy

from splink.internals.column_expression import (
    ColumnExpression as SplinkColumnExpression,
)
from splink.internals.dialects import SplinkDialect

from .dialect import ClickhouseDialect


class ColumnExpression(SplinkColumnExpression):
    def __init__(self, sql_expression: str):
        super().__init__(sql_expression=sql_expression, sql_dialect=ClickhouseDialect())

    def _parse_date_to_int_dialected(
        self, name: str, sql_dialect: SplinkDialect
    ) -> str:
        # need to have sql_dialect passed, even if it does nothing
        # parent requires this to be in function signature

        return f"days_since_epoch({name})"

    def parse_date_to_int(self) -> "ColumnExpression":
        """
        Parses date string to an integer, representing days since
        the Unix epoch (1970-01-01).
        """
        clone = self._clone()
        clone.operations.append(clone._parse_date_to_int_dialected)
        return clone

    @staticmethod
    def from_base_expression(
        column_expression: SplinkColumnExpression,
    ) -> "ColumnExpression":
        new_expression = ColumnExpression(
            sql_expression=column_expression.raw_sql_expression
        )
        new_expression.operations = copy(column_expression.operations)
        return new_expression
