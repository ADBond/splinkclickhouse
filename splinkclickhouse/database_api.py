from abc import abstractmethod
from typing import Optional

import pandas as pd
from splink.internals.database_api import DatabaseAPI

from .custom_sql import days_since_epoch_sql
from .dialect import ClickhouseDialect


class ClickhouseAPI(DatabaseAPI[None]):
    sql_dialect = ClickhouseDialect()

    @property
    def database(self) -> Optional[str]:
        return None

    @abstractmethod
    def _get_results_from_backend(self, sql: str):
        pass

    def _coerce_input_to_pd_if_needed(self, input):
        if isinstance(input, dict):
            input = pd.DataFrame(input)
        elif isinstance(input, list):
            input = pd.DataFrame.from_records(input)
        return input

    def _information_schema_query(
        self,
        column_name: str,
        information_schema_table_name: str,
        table_name: str,
        schema_name: Optional[str] = None,
    ):
        and_if_needed = (
            f"AND table_schema = '{schema_name}'" if schema_name is not None else ""
        )
        return f"""
            SELECT {column_name}
            FROM information_schema.{information_schema_table_name}
            WHERE table_name = '{table_name}'
            {and_if_needed}
        """

    @property
    def _core_replacements(self) -> list[tuple[str, str]]:
        return [
            ("float8", "Float64"),
            # workaround for https://github.com/ClickHouse/ClickHouse/issues/61004
            ("count(*)", "count()"),
            ("COUNT(*)", "COUNT()"),
            # TODO: very sorry for this
            # avoids 'double selection' issue in creating __splink__block_counts
            (", count_l, count_r,", ","),
            (
                "SELECT DISTINCT r.representative",
                "SELECT DISTINCT r.representative AS representative",
            ),
        ]

    @property
    def _specific_replacements(self) -> list[tuple[str, str]]:
        return []

    # some excessively brittle SQL replacements to handle Clickhouse name-resolution
    # and other dialect quirks
    @property
    def _sql_replacements(self) -> list[tuple[str, str]]:
        return self._core_replacements + self._specific_replacements

    def _setup_for_execute_sql(self, sql: str, physical_name: str) -> str:
        self.delete_table_from_database(physical_name)
        for old_sql, new_sql in self._sql_replacements:
            sql = sql.replace(old_sql, new_sql)

        sql = f"CREATE TABLE {physical_name} ORDER BY tuple() AS {sql}"
        return sql

    # alias random -> rand. Need this function for comparison viewer
    def _create_random_function(self) -> None:
        self._execute_sql_against_backend(
            "CREATE FUNCTION IF NOT EXISTS random AS () -> rand()"
        )

    def _register_custom_udfs(self) -> None:
        self._execute_sql_against_backend(
            f"""
            CREATE FUNCTION IF NOT EXISTS
                days_since_epoch AS
                (date_string) -> {days_since_epoch_sql}
            """
        )
