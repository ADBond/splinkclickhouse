from typing import TYPE_CHECKING

from splink.internals.input_column import InputColumn
from splink.internals.splink_dataframe import SplinkDataFrame

if TYPE_CHECKING:
    from .database_api import ChDBAPI


class ClickhouseDataFrame(SplinkDataFrame):


    def _drop_table_from_database(self, force_non_splink_table=False):
        self._check_drop_table_created_by_splink(force_non_splink_table)
        self.db_api.delete_table_from_database(self.physical_name)

