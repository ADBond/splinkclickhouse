from typing import Any

from .clickhouse_server.database_api import ClickhouseServerAPI

__version__ = "0.3.4"


# Use getarr to make the error appear at the point of use
def __getattr__(name: str) -> Any:
    try:
        if name == "ChDBAPI":
            from .chdb.database_api import ChDBAPI

            return ChDBAPI
    except ImportError as err:
        if name == "ChDBAPI":
            raise ImportError(
                f"'{name}' cannot be imported because its dependencies are not "
                "installed. To get these please install with the 'chdb' extras: "
                "`pip install splinkclickhouse[chdb]`."
            ) from err
    raise ImportError(f"cannot import name '{name}' from splinkclickhouse") from None


__all__ = ["ChDBAPI", "ClickhouseServerAPI"]
