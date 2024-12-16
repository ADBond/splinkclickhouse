from splink.internals.database_api import DatabaseAPI

from .dialect import ClickhouseDialect


class ClickhouseAPI(DatabaseAPI[None]):
    sql_dialect = ClickhouseDialect()

