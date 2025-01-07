[![pypi](https://img.shields.io/github/v/release/adbond/splinkclickhouse?include_prereleases)](https://pypi.org/project/splinkclickhouse/#history)
[![Downloads](https://static.pepy.tech/badge/splinkclickhouse)](https://pepy.tech/project/splinkclickhouse)
[![codecov](https://codecov.io/github/adbond/splinkclickhouse/graph/badge.svg?token=NUHM8IPJL4)](https://codecov.io/github/adbond/splinkclickhouse)

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

See the docs [TODO](TODO).

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
