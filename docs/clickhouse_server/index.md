# Clickhouse Server

The primary way to use `splinkclickhouse` is with data in a running Clickhouse server.

## Connecting to Splink

To use Clickhouse with Splink you will need to connect to your Clickhouse instance with [clickhouse-connect](https://github.com/ClickHouse/clickhouse-connect).

You will need to configure a client to your running version, and use this to create a [Splink DatabaseAPI]

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

From this point onwards your code should generally be the same as that appearing in [the Splink docs](https://moj-analytical-services.github.io/splink/demos/examples/examples_index.html). The exceptions will be if you want to take advantage of [Clickhouse-specific comparisons](../api/libraries.md) or need [advanced usage](./advanced.md).
