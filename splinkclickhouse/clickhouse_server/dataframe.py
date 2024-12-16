# need this for annotating db_api:
from __future__ import annotations

from typing import TYPE_CHECKING

from ..dataframe import ClickhouseDataFrame

if TYPE_CHECKING:
    from .database_api import ClickhouseServerAPI


class ClickhouseServerDataFrame(ClickhouseDataFrame):
    db_api: ClickhouseServerAPI

    def __init__(self, df_name, physical_name, db_api):
        super().__init__(df_name, physical_name, db_api)

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
