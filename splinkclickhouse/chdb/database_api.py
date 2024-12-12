import logging

import chdb.dbapi as chdb_dbapi
import pandas as pd
from splink.internals.database_api import DatabaseAPI

from ..custom_sql import days_since_epoch_sql
from ..dialect import ClickhouseDialect
from .dataframe import ChDBDataFrame

logger = logging.getLogger(__name__)


class ChDBAPI(DatabaseAPI[None]):
    sql_dialect = ClickhouseDialect()

    def __init__(
        self,
        con: chdb_dbapi.Connection,
        schema: str = "splink",
        register_custom_udfs: bool = True,
    ):
        super().__init__()

        self.con = con
        self._db_schema = schema

        self._create_splink_schema()
        self._create_random_function()
        if register_custom_udfs:
            self._register_custom_udfs()

    def _table_registration(self, input, table_name):
        if isinstance(input, dict):
            input = pd.DataFrame(input)
        elif isinstance(input, list):
            input = pd.DataFrame.from_records(input)

        # chdb currently needs pandas indices to start at 0
        # see https://github.com/chdb-io/chdb/issues/282
        # reset the index if not the case, but otherwise leave alone
        # TODO: remove this workaround once chdb issue is resolved
        try:
            input[0]
        except KeyError:
            input = input.reset_index()
        cursor = self._get_cursor()
        sql = (
            f"CREATE OR REPLACE TABLE {self._db_schema}.{table_name} "
            "ORDER BY tuple() "
            f"AS SELECT * FROM Python(input);"
        )
        try:
            cursor.execute(sql)
        finally:
            # whatever happens, close the cursor
            self._reset_cursor(cursor)

    def table_to_splink_dataframe(self, templated_name, physical_name):
        return ChDBDataFrame(templated_name, physical_name, self)

    def table_exists_in_database(self, table_name):
        sql = f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_name = '{table_name}';
        """

        cursor = self._get_cursor()
        try:
            cursor.execute(sql)
            table_name_row = cursor.fetchone()
        finally:
            self._reset_cursor(cursor)
        return table_name_row is not None

    def _setup_for_execute_sql(self, sql: str, physical_name: str) -> str:
        self.delete_table_from_database(physical_name)
        sql = sql.replace("float8", "Float64")
        # TODO: horrible hack
        # can't seem to set union_default_mode for some reason
        sql = sql.replace("UNION ALL", "__tmp__ua__")
        sql = sql.replace("UNION", "UNION DISTINCT")
        sql = sql.replace("__tmp__ua__", "UNION ALL")
        # workaround for https://github.com/ClickHouse/ClickHouse/issues/61004
        sql = sql.replace("count(*)", "count()")
        sql = sql.replace("COUNT(*)", "COUNT()")
        # TODO: very sorry for this
        # avoids 'double selection' issue in creating __splink__block_counts
        sql = sql.replace(", count_l, count_r,", ",")
        # some excessively brittle SQL replacements to hand Clickhouse name-resolution
        sql = sql.replace(
            "SELECT DISTINCT r.representative",
            "SELECT DISTINCT r.representative AS representative",
        )

        sql = f"CREATE TABLE {physical_name} ORDER BY tuple() AS {sql}"
        return sql

    def _execute_sql_against_backend(
        self, final_sql: str, templated_name: str = None, physical_name: str = None
    ) -> None:
        cursor = self._get_cursor()
        try:
            cursor.execute(final_sql)
        finally:
            self._reset_cursor(cursor)
        return None

    def _get_cursor(self) -> chdb_dbapi.cursors.DictCursor:
        return self.con.cursor(chdb_dbapi.cursors.DictCursor)

    def _reset_cursor(self, cursor):
        cursor.close()

    def _create_splink_schema(self):
        sql = f"""
        CREATE DATABASE IF NOT EXISTS {self._db_schema};
        USE {self._db_schema};
        """
        self._execute_sql_against_backend(sql)

    # alias random -> rand. Need this function for comparison viewer
    def _create_random_function(self) -> None:
        sql = "CREATE FUNCTION IF NOT EXISTS random AS () -> rand()"

        cursor = self._get_cursor()
        try:
            cursor.execute(sql)
        finally:
            self._reset_cursor(cursor)

    def _register_custom_udfs(self) -> None:
        sql = f"""
        CREATE FUNCTION IF NOT EXISTS
            days_since_epoch AS
            (date_string) -> {days_since_epoch_sql}
        """

        cursor = self._get_cursor()
        try:
            cursor.execute(sql)
        finally:
            self._reset_cursor(cursor)
