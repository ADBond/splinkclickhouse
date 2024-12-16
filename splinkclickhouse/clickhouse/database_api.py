import logging

import pandas as pd
from clickhouse_connect.driver.client import Client

from ..custom_sql import days_since_epoch_sql
from ..database_api import ClickhouseAPI
from .dataframe import ClickhouseDataFrame

logger = logging.getLogger(__name__)


class ClickhouseServerAPI(ClickhouseAPI):

    def __init__(
        self,
        client: Client,
        register_custom_udfs: bool = True,
    ):
        super().__init__()

        self.client = client
        self.set_union_default_mode()
        self._create_random_function()
        if register_custom_udfs:
            self._register_custom_udfs()

    def _table_registration(self, input, table_name) -> None:
        if isinstance(input, pd.DataFrame):
            sql = self._create_table_from_pandas_frame(input, table_name)
            self.client.query(sql)
            self.client.insert_df(table_name, input)
        elif isinstance(input, str):
            sql = (
                f"CREATE OR REPLACE TABLE {table_name} "
                "ORDER BY tuple() "
                f"AS SELECT * FROM {input}"
            )
            self.client.query(sql)
        else:
            raise TypeError(
                "ClickhouseServerAPI currently only accepts table names (str) "
                "or pandas DataFrames as inputs for table registration. "
                f"Received type {type(input)}"
            )

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
    ):
        self.client.query(final_sql)

    @property
    def database(self) -> str:
        return self.client.database or "default"

    def _execute_utility_sql(self, sql: str) -> None:
        self.client.command(sql)

    # Clickhouse can not handle a bare 'UNION' by default
    # we can set desired behaviour for the session by executing this
    def set_union_default_mode(self) -> None:
        self._execute_utility_sql("SET union_default_mode = 'DISTINCT'")

    def _create_table_from_pandas_frame(self, df: pd.DataFrame, table_name: str) -> str:
        sql = f"CREATE OR REPLACE TABLE {table_name} ("

        first_col = True
        for column_name in df.columns:
            if not first_col:
                sql += ", "
            column = df[column_name]
            col_type = column.dtype
            first_col = False

            if pd.api.types.is_integer_dtype(col_type):
                sql += f"{column_name} Nullable(UInt32)"
            elif pd.api.types.is_float_dtype(col_type):
                sql += f"{column_name} Nullable(Float64)"
            elif pd.api.types.is_list_like(column[0]):
                sql += f"{column_name} Array(String)"
            elif pd.api.types.is_string_dtype(col_type):
                sql += f"{column_name} Nullable(String)"
            else:
                raise ValueError(f"Unknown data type {col_type}")

        sql += ") ENGINE MergeTree ORDER BY tuple()"

        return sql
