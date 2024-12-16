# need this for annotating db_api:
from __future__ import annotations

from typing import TYPE_CHECKING

from splink.internals.input_column import InputColumn

from ..dataframe import ClickhouseDataFrame

if TYPE_CHECKING:
    from .database_api import ClickhouseServerAPI


class ClickhouseServerDataFrame(ClickhouseDataFrame):
    db_api: ClickhouseServerAPI

    def __init__(self, df_name, physical_name, db_api):
        super().__init__(df_name, physical_name, db_api)





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

        res = self.db_api.client.query(sql)
        return list(res.named_results())
