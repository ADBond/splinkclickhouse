# need this for annotating db_api:
from __future__ import annotations

from typing import TYPE_CHECKING

from ..dataframe import ClickhouseDataFrame

if TYPE_CHECKING:
    from .database_api import ChDBAPI


class ChDBDataFrame(ClickhouseDataFrame):
    db_api: ChDBAPI

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
