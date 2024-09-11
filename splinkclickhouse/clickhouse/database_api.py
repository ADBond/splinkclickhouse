import logging

from clickhouse_connect.driver.client import Client
from splink.internals.database_api import DatabaseAPI

from ..dialect import ClickhouseDialect
from .dataframe import ClickhouseDataFrame

logger = logging.getLogger(__name__)


class ClickhouseAPI(DatabaseAPI[None]):
    sql_dialect = ClickhouseDialect()

    def __init__(
        self,
        client: Client,
    ):
        super().__init__()

        self.client = client
        client.command("SET union_default_mode = 'DISTINCT'")

    def _table_registration(self, input, table_name):
        if not isinstance(input, str):
            raise TypeError(
                "ClickhouseAPI currently only accepts table names (str) "
                "as inputs for table registration"
            )

        sql = (
            f"CREATE OR REPLACE TABLE {table_name} "
            "ORDER BY tuple() "
            f"AS SELECT * FROM {input}"
        )
        self.client.query(sql)

    def table_to_splink_dataframe(self, templated_name, physical_name):
        return ClickhouseDataFrame(templated_name, physical_name, self)

    def table_exists_in_database(self, table_name):
        sql = f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_name = '{table_name}'
        AND table_schema = '{self.database}'
        """

        res = self.client.query(sql).result_set
        return len(res) > 0

    def _setup_for_execute_sql(self, sql: str, physical_name: str) -> str:
        self.delete_table_from_database(physical_name)
        sql = sql.replace("float8", "Float64")

        sql = f"CREATE TABLE {physical_name} ORDER BY tuple() AS {sql}"
        return sql

    def _execute_sql_against_backend(
        self, final_sql: str, templated_name: str = None, physical_name: str = None
    ):
        return self.client.query(final_sql)

    @property
    def database(self):
        return self.client.database or "default"
