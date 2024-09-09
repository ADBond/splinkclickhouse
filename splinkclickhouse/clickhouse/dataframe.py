from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from splink.internals.input_column import InputColumn
from splink.internals.splink_dataframe import SplinkDataFrame

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from .database_api import ClickhouseAPI


class ClickhouseDataFrame(SplinkDataFrame):
    db_api: ClickhouseAPI

    def __init__(self, df_name, physical_name, db_api):
        super().__init__(df_name, physical_name, db_api)

    @property
    def columns(self) -> list[InputColumn]:
        sql = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{self.physical_name}'
        """

        client = self.db_api.client
        res = client.query(sql).named_results()
        cols = [r["column_name"] for r in res]

        return [InputColumn(c, sql_dialect="clickhouse") for c in cols]

    def validate(self):
        if not self.db_api.table_exists_in_database(self.physical_name):
            raise ValueError(f"{self.physical_name} does not exist in the db provided.")

    def _drop_table_from_database(self, force_non_splink_table=False):
        self._check_drop_table_created_by_splink(force_non_splink_table)
        self.db_api.delete_table_from_database(self.physical_name)

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
