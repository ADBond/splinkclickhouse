import chdb.dbapi as chdb_dbapi
import pandas as pd

from ..database_api import ClickhouseAPI
from .dataframe import ChDBDataFrame


class ChDBAPI(ClickhouseAPI):
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
        sql = (
            f"CREATE OR REPLACE TABLE {self._db_schema}.{table_name} "
            "ORDER BY tuple() "
            f"AS SELECT * FROM Python(input);"
        )
        self._execute_sql_against_backend(sql)

    def table_to_splink_dataframe(self, templated_name, physical_name):
        return ChDBDataFrame(templated_name, physical_name, self)

    def table_exists_in_database(self, table_name):
        sql = self._information_schema_query(
            "table_name", "tables", table_name, self.database
        )

        cursor = self._get_cursor()
        try:
            cursor.execute(sql)
            table_name_row = cursor.fetchone()
        finally:
            self._reset_cursor(cursor)
        return table_name_row is not None

    @property
    def _specific_replacements(self) -> list[tuple[str, str]]:
        return [
            # TODO: horrible hack
            # can't seem to set union_default_mode for some reason
            ("UNION ALL", "__tmp__ua__"),
            ("UNION", "UNION DISTINCT"),
            ("__tmp__ua__", "UNION ALL"),
        ]

    def _execute_sql_against_backend(
        self, final_sql: str, templated_name: str = None, physical_name: str = None
    ) -> None:
        cursor = self._get_cursor()
        try:
            cursor.execute(final_sql)
        finally:
            self._reset_cursor(cursor)
        return None

    def _get_results_from_backend(self, sql: str):
        cursor = self._get_cursor()
        try:
            cursor.execute(sql)
            res = cursor.fetchall()
        finally:
            self._reset_cursor(cursor)
        return res

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
