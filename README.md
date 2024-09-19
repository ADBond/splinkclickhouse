# `splinkclickhouse`

Basic [Clickhouse](https://clickhouse.com/docs/en/intro) support for use as a backend with the data-linkage and deduplication package [Splink](https://moj-analytical-services.github.io/splink/).

Supports in-process [chDB](https://clickhouse.com/docs/en/chdb) version or a clickhouse server connected via [clickhouse connect](https://clickhouse.com/docs/en/integrations/python).

## Installation

Install from `PyPI` using `pip`:

```sh
pip install splinkclickhouse
```

Alternatively you can install the package from github:

```sh
pip install git+https://github.com/ADBond/splinkclickhouse.git@v0.2.4
# Replace with any version you want, or specify a branch after '@'
```

## Use

### `chDB`

Import `ChDBAPI`, which accepts a connection from `chdb.api`:
```python
import splink.comparison_library as cl
from chdb import dbapi
from splink import Linker, SettingsCreator, block_on, splink_datasets

from splinkclickhouse import ChDBAPI

con = dbapi.connect()
db_api = ChDBAPI(con)

df = splink_datasets.fake_1000

settings = SettingsCreator(
    link_type="dedupe_only",
    comparisons=[
        cl.NameComparison("first_name"),
        cl.JaroAtThresholds("surname"),
        cl.DateOfBirthComparison(
            "dob",
            input_is_string=True,
        ),
        cl.DamerauLevenshteinAtThresholds("city").configure(
            term_frequency_adjustments=True
        ),
        cl.EmailComparison("email"),
    ],
    blocking_rules_to_generate_predictions=[
        block_on("first_name", "dob"),
        block_on("surname"),
    ],
)

linker = Linker(df, settings, db_api=db_api)
```

See [Splink documentation](https://moj-analytical-services.github.io/splink/) for use of the `Linker`.

### Clickhouse server

Import `ClickhouseAPI`, which accepts a `clickhouse_connect` client, configured with attributes relevant for your connection:
```python
import clickhouse_connect
import splink.comparison_library as cl
from splink import Linker, SettingsCreator, block_on, splink_datasets

from splinkclickhouse import ClickhouseAPI

df = splink_datasets.fake_1000

conn_atts = {
    "host": "localhost",
    "port": 8123,
    "username": "splinkognito",
    "password": "splink123!",
}

db_name = "__temp_splink_db"

default_client = clickhouse_connect.get_client(**conn_atts)
default_client.command(f"CREATE DATABASE IF NOT EXISTS {db_name}")
client = clickhouse_connect.get_client(
    **conn_atts,
    database=db_name,
)

db_api = ClickhouseAPI(client)

# can have at most one tf-adjusted comparison, see caveats below
settings = SettingsCreator(
    link_type="dedupe_only",
    comparisons=[
        cl.JaroWinklerAtThresholds("first_name"),
        cl.JaroAtThresholds("surname"),
        cl.DateOfBirthComparison(
            "dob",
            input_is_string=True,
        ),
        cl.DamerauLevenshteinAtThresholds("city").configure(
            term_frequency_adjustments=True
        ),
        cl.JaccardAtThresholds("email"),
    ],
    blocking_rules_to_generate_predictions=[
        block_on("first_name", "dob"),
        block_on("surname"),
    ],
)

linker = Linker(df, settings, db_api=db_api)
```

See [Splink documentation](https://moj-analytical-services.github.io/splink/) for use of the `Linker`.

### Comparisons

`splinkclickhouse` is compatible with all of the in-built `splinks` comparisons and comparison levels in `splink.comparison_library` and `splink.comparison_level_library`.
However, `splinkclickhouse ` provides a few pre-made extras to leverage Clickhouse-specific functionality.
These can be used in exactly the same way as the native Splink libraries, for example:

```python
import splink.comparison_library as cl
from splink import SettingsCreator

import splinkclickhouse.comparison_library as cl_ch

...
settings = SettingsCreator(
    link_type="dedupe_only",
    comparisons=[
        cl.ExactMatch("name"),
        cl_ch.DistanceInKMAtThresholds(
            "latitude",
            "longitude",
            [10, 50, 100, 200, 500],
        ),
    ],
)
```

or with individual comparison-levels:

```python
import splink.comparison_level_library as cll
import splink.comparison_library as cl
from splink import SettingsCreator

import splinkclickhouse.comparison_level_library as cll_ch

...
settings = SettingsCreator(
    link_type="dedupe_only",
    comparisons=[
        cl.ExactMatch("name"),
        cl.CustomComparison(
            comparison_levels = [
                cll.And(
                    cll.NullLevel("city"),
                    cll.NullLevel("postcode"),
                    cll.Or(cll.NullLevel("latitude"), cll.NullLevel("longitude"))
                ),
                cll.ExactMatch("postcode"),
                cll_ch.DistanceInKMLevel("latitude", "longitude", 5),
                cll_ch.DistanceInKMLevel("latitude", "longitude", 10),
                cll.ExactMatch("city"),
                cll_ch.DistanceInKMLevel("latitude", "longitude", 50),
                cll.ElseLevel(),
            ],
            output_column_name="location",
        ),
    ],
)
```

## Known issues / caveats

### Datetime parsing

Clickhouse offers several different date formats.
The basic `Date` format cannot handle dates before the epoch (1970-01-01), which makes it unsuitable for many use-cases for holding date-of-births.

The parsing function `parseDateTime` (and variants) which support providing custom formats return a `DateTime`, which also has the above limited range.
In `splinkclickhouse` we use the function `parseDateTime64BestEffortOrNull` so that we can use the extended-range `DateTime64` data type, which supports dates back to 1900-01-01, but does not allow custom date formats. Currently no `DateTime64` equivalent of `parseDateTime` exists.

If you require different behaviour (for instance if you have an unusual date format and know that you do not need dates outside of the `DateTime` range) you will either need to derive a new column in your source data, or construct the relevant SQL expression manually.

There is not currently a way in Clickhouse to deal directly with date values before 1900 - if you require such values you will have to manually process these to a different type, and construct the relevant SQL logic.

### `NULL` values in `chdb`

When passing data into `chdb` from pandas or pyarrow tables, `NULL` values in `String` columns are converted into empty strings, instead of remaining `NULL`.

For now this is not handled within the package. You can workaround the issue by wrapping column names in `NULLIF`:

```python
import splink.comparison_level as cl

first_name_comparison = cl.DamerauLevenshteinAtThresholds("NULLIF(first_name, '')")
```

### Term-frequency adjustments

Currently at most one term frequency adjustment can be used with `ClickhouseAPI`.

This also applies to `ChDBAPI` but _only in `debug_mode`_. With `debug_mode` off there is no limit on term frequency adjustments.

### `ClickhouseAPI` pandas registration

`ClickhouseAPI` will allow registration of pandas dataframes, by inferring the types of columns. It currently only does this for string, integer, and float columns, and will always make them `Nullable`.

If you require other data types, or more fine-grained control, it is recommended to import the data into Clickhouse yourself, and then pass the table name (as a string) to the `Linker` instead.
