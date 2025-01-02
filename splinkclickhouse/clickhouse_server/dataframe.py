# need this for annotating db_api:
from __future__ import annotations

from typing import TYPE_CHECKING

from ..dataframe import ClickhouseDataFrame

if TYPE_CHECKING:  # pragma: no cover
    from .database_api import ClickhouseServerAPI


class ClickhouseServerDataFrame(ClickhouseDataFrame):
    db_api: ClickhouseServerAPI
