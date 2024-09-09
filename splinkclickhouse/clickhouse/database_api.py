import logging

import pandas as pd
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

    def _table_registration(self, input, table_name):
        if isinstance(input, dict):
            input = pd.DataFrame(input)
        elif isinstance(input, list):
            input = pd.DataFrame.from_records(input)

        sql = (
            f"CREATE OR REPLACE TABLE {self._db_schema}.{table_name} "
            "ORDER BY tuple() "
            f"AS SELECT * FROM Python(input);"
        )
        self.client.query(sql)

    def table_to_splink_dataframe(self, templated_name, physical_name):
        return ClickhouseDataFrame(templated_name, physical_name, self)

    def table_exists_in_database(self, table_name):
        sql = f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_name = '{table_name}'
        """

        res = self.client.query(sql).result_set
        return len(res) > 0

    def _setup_for_execute_sql(self, sql: str, physical_name: str) -> str:
        self.delete_table_from_database(physical_name)
        sql = sql.replace("float8", "Float64")
        # TODO: horrible hack
        # can't seem to set union_default_mode for some reason
        sql = sql.replace("UNION ALL", "__tmp__ua__")
        sql = sql.replace("UNION", "UNION DISTINCT")
        sql = sql.replace("__tmp__ua__", "UNION ALL")
        # TODO: I'm not serious with this:
        sql = sql.replace(", count_l, count_r,", ",")

        sql = f"CREATE TABLE {physical_name} ORDER BY tuple() AS {sql}"
        return sql

    def _execute_sql_against_backend(
        self, final_sql: str, templated_name: str = None, physical_name: str = None
    ):
        return self.client.query(final_sql)
