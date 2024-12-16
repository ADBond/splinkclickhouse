# need this for annotating db_api:
from __future__ import annotations

from typing import TYPE_CHECKING

from splink.internals.input_column import InputColumn

from ..dataframe import ClickhouseDataFrame

if TYPE_CHECKING:
    from .database_api import ChDBAPI


class ChDBDataFrame(ClickhouseDataFrame):
    db_api: ChDBAPI

    def __init__(self, df_name, physical_name, db_api):
        super().__init__(df_name, physical_name, db_api)
        self._db_schema = db_api._db_schema

    @property
    def columns(self) -> list[InputColumn]:
        sql = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{self.physical_name}';
        """

        cursor = self.db_api._get_cursor()
        try:
            cursor.execute(sql)
            res = cursor.fetchall()
        finally:
            self.db_api._reset_cursor(cursor)
        cols = [r["column_name"] for r in res]

        return [InputColumn(c, sqlglot_dialect_str="clickhouse") for c in cols]

    def validate(self):
        if not self.db_api.table_exists_in_database(self.physical_name):
            raise ValueError(f"{self.physical_name} does not exist in the db provided.")

    def as_record_dict(self, limit=None):
        sql = f"""
        SELECT *
        FROM {self.physical_name}
        """
        if limit:
            sql += f" LIMIT {limit}"
        sql += ";"

        cursor = self.db_api._get_cursor()
        try:
            cursor.execute(sql)
            res = cursor.fetchall()
        finally:
            self.db_api._reset_cursor(cursor)
        return res
