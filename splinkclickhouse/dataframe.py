from splink.internals.input_column import InputColumn
from splink.internals.splink_dataframe import SplinkDataFrame


class ClickhouseDataFrame(SplinkDataFrame):
    def __init__(self, df_name, physical_name, db_api):
        super().__init__(df_name, physical_name, db_api)

    @property
    def columns(self) -> list[InputColumn]:
        sql = self.db_api._information_schema_query(
            "column_name", "columns", self.physical_name, self.db_api.database
        )
        res = self.db_api._get_results_from_backend(sql)

        cols = [r["column_name"] for r in res]

        return [InputColumn(c, sqlglot_dialect_str="clickhouse") for c in cols]

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

        res = self.db_api._get_results_from_backend(sql)
        return list(res)
