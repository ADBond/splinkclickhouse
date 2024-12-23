[![pypi](https://img.shields.io/github/v/release/adbond/splinkclickhouse?include_prereleases)](https://pypi.org/project/splinkclickhouse/#history)
[![Downloads](https://static.pepy.tech/badge/splinkclickhouse)](https://pepy.tech/project/splinkclickhouse)

# `splinkclickhouse`

Basic [Clickhouse](https://clickhouse.com/docs/en/intro) support for use as a backend with the data-linkage and deduplication package [Splink](https://moj-analytical-services.github.io/splink/).

Supports clickhouse server connected via [clickhouse connect](https://clickhouse.com/docs/en/integrations/python).

Also supports in-process [chDB](https://clickhouse.com/docs/en/chdb) version if installed with the `chdb` extras.

## Installation

Install from `PyPI` using `pip`:

```sh
# just installs the Clickhouse server dependencies
pip install splinkclickhouse
# or to install with support for chdb:
pip install splinkclickhouse[chdb]
```

or you can install the package directly from github:

```sh
# Replace with any version you want, or specify a branch after '@'
pip install git+https://github.com/ADBond/splinkclickhouse.git@v0.4.0
```

If instead you are using `conda`, `splinkclickhouse` is available on [conda-forge](https://conda-forge.org/):

```sh
conda install conda-forge::splinkclickhouse
```

Note that the `conda` version will only be able to use [the Clickhouse server functionality](#clickhouse-server) as `chdb` is not currently available within `conda`.

### Caveats

While the package is in early development there will may be breaking changes in new versions without warning, although these _should_ only occur in new minor versions.
Nevertheless if you depend on this package it is recommended to pin a version to avoid any disruption that this may cause.

It is tested against Clickhouse server version 24.8.
There have also been occasional tests against 24.11.
Other versions are likely to function normally, but if you have a significantly different version, functionality may be affected.

### Dev setup

For dev setup see [dev.md](./dev.md).

## Use

### Clickhouse server

Import `ClickhouseServerAPI`, which accepts a `clickhouse_connect` client, configured with attributes relevant for your connection:
```python
import clickhouse_connect
import splink.comparison_library as cl
from splink import Linker, SettingsCreator, block_on, splink_datasets

from splinkclickhouse import ClickhouseServerAPI

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

db_api = ClickhouseServerAPI(client)

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

### `chDB`

To use `chdb` as a Splink backend you must install the `chdb` package.
This is automatically installed if you install with the `chdb` extras (`pip install splinkclickhouse[chdb]`).

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

## Support

If you have difficulties with the package you can [open an issue](https://github.com/ADBond/splinkclickhouse/issues).
You may also [suggest changes by opening a PR](https://github.com/ADBond/splinkclickhouse/pulls), although it may be best to discuss in an issue beforehand.

This package is 'unofficial', in that it is not directly supported by the Splink team. Maintenance / improvements will be done on a 'best effort' basis where resources allow.

## Known issues / caveats

### Datetime parsing

Clickhouse offers several different date formats.
The basic `Date` format cannot handle dates before the Unix epoch (1970-01-01), which makes it unsuitable for many use-cases for holding date-of-births.

The parsing function `parseDateTime` (and variants) which support providing custom formats return a `DateTime`, which also has the above limited range.
In `splinkclickhouse` we use the function `parseDateTime64BestEffortOrNull` so that we can use the extended-range `DateTime64` data type, which supports dates back to 1900-01-01, but does not allow custom date formats. Currently no `DateTime64` equivalent of `parseDateTime` exists.

If you require different behaviour (for instance if you have an unusual date format and know that you do not need dates outside of the `DateTime` range) you will either need to derive a new column in your source data, or construct the relevant SQL expression manually.

#### Extended Dates

There is not currently a way in Clickhouse to deal directly with date values before 1900. However, `splinkclickhouse` offers some tools to help with this.
It creates a SQL UDF (which can be opted-out of) `days_since_epoch`, to convert a date string (in `YYYY-MM-DD` format) into an integer, representing the number of days since `1970-01-01` to handle dates well outside the range of `DateTime64`, based on the proleptic Gregorian calendar.

This can be used with column expression extension `splinkclickhouse.column_expression.ColumnExpression` via the transform `.parse_date_to_int()`, or using custom versions of Splink library functions `cll.AbsoluteDateDifferenceLevel`, `cl.AbsoluteDateDifferenceAtThresholds`, and `cl.DateOfBirthComparison`.
These functions can be used with string columns (which will be wrapped in the above parsing function), or integer columns if the conversion via `days_since_epoch` is already done in the data-preparation stage.

### `NULL` values in `chdb`

When passing data into `chdb` from pandas or pyarrow tables, `NULL` values in `String` columns are converted into empty strings, instead of remaining `NULL`.

For now this is not handled within the package. You can workaround the issue by wrapping column names in `NULLIF`:

```python
import splink.comparison_level as cl

first_name_comparison = cl.DamerauLevenshteinAtThresholds("NULLIF(first_name, '')")
```

### `ClickhouseServerAPI` pandas registration

`ClickhouseServerAPI` will allow registration of pandas dataframes, by inferring the types of columns. It currently only does this for string, integer, and float columns, and will always make them `Nullable`.

If you require other data types, or more fine-grained control, it is recommended to import the data into Clickhouse yourself, and then pass the table name (as a string) to the `Linker` instead.
