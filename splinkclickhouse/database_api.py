from abc import abstractmethod

from splink.internals.database_api import DatabaseAPI

from .custom_sql import days_since_epoch_sql
from .dialect import ClickhouseDialect


class ClickhouseAPI(DatabaseAPI[None]):
    sql_dialect = ClickhouseDialect()



    @abstractmethod
    def _execute_utility_sql(self, sql: str) -> None:
        pass

    # alias random -> rand. Need this function for comparison viewer
    def _create_random_function(self) -> None:
        self._execute_utility_sql("CREATE FUNCTION IF NOT EXISTS random AS () -> rand()")

    def _register_custom_udfs(self) -> None:
        self._execute_utility_sql(
            f"""
            CREATE FUNCTION IF NOT EXISTS
                days_since_epoch AS
                (date_string) -> {days_since_epoch_sql}
            """
        )
