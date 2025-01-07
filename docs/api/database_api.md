# DatabaseAPI

A Splink `DatabaseAPI` is the object that allows Splink to communicate with a SQL backend.

`splinkclickhouse` has two versions available, depending on which mode you are working in.

## ClickhouseServerAPI

Set up a `ClickhouseServerAPI` by providing a client configured to your instance:
```python
import clickhouse_connect

from splinkclickhouse import ClickhouseServerAPI

client = clickhouse_connect.get_client(
    host="127.0.0.1",
    port=8443,
    username="splink_user",
    password="password",
    database="database",
)

db_api = ClickhouseServerAPI(client)
```

### Data ingestion

It is recommended that any data you wish to deduplicate/link with Splink you load into Clickhouse yourself. You will then just use the names of tables in the database when you need to reference them.

Additionally `ClickhouseServerAPI` can process [`pandas.DataFrame`s](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html), which can be useful for trying out ideas or playing around. This will try to infer appropriate types on a 'best effort' basis, but may well get things wrong, particularly for more complex types, so should not be relied upon.

You can pass a pandas frame anywhere that Splink expects a table, or instead you can register it once and refer to it by name:
```python
import clickhouse_connect
from splink import splink_datasets

from splinkclickhouse import ClickhouseServerAPI


client = clickhouse_connect.get_client(
    host="localhost",
    port=8123,
    username="user",
    password="password",
    database=db_name,
)
db_api = ClickhouseServerAPI(client)

df = splink_datasets.fake_1000
db_api.register_table(df, "fake_1000_people")
# 'fake_1000_people' will now be registered in your database, and you can refer to this for further Splink operations
```

::: splinkclickhouse.clickhouse_server.database_api.ClickhouseServerAPI
