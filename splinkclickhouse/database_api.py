from abc import abstractmethod

from splink.internals.database_api import DatabaseAPI

from .custom_sql import days_since_epoch_sql
from .dialect import ClickhouseDialect


class ClickhouseAPI(DatabaseAPI[None]):
    sql_dialect = ClickhouseDialect()


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
            # some excessively brittle SQL replacements to hand Clickhouse name-resolution
            (
                "SELECT DISTINCT r.representative",
                "SELECT DISTINCT r.representative AS representative",
            ),
        ]

    @property
    def _specific_replacements(self) -> list[tuple[str, str]]:
        return []

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
        self._execute_sql_against_backend("CREATE FUNCTION IF NOT EXISTS random AS () -> rand()")

    def _register_custom_udfs(self) -> None:
        self._execute_sql_against_backend(
            f"""
            CREATE FUNCTION IF NOT EXISTS
                days_since_epoch AS
                (date_string) -> {days_since_epoch_sql}
            """
        )
