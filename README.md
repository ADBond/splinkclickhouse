# `splinkclickhouse`

Basic [Clickhouse](https://clickhouse.com/docs/en/intro) support for use as a backend with the data-linkage and deduplication package [Splink](https://moj-analytical-services.github.io/splink/).

Supports in-process [chDB](https://clickhouse.com/docs/en/chdb) version or a clickhouse instance connected via [clickhouse connect](https://clickhouse.com/docs/en/integrations/python).

## Using

### ChDB

Import the relevant api:

```python
from splinkclickhouse import ChDBAPI
```

See [getting started script](./scripts/getting_started_chdb.py) for example of use:

```sh
poetry run python scripts/getting_started_chdb.py
```

### Clickhouse instance

Import the relevant api:

```python
from splinkclickhouse import ClickhouseAPI
```

You can run a local instance in docker with provided docker-compose file:

```sh
docker-compose -f scripts/docker-compose.yaml up
```

See [getting started script](./scripts/getting_started_clickhouse.py) for example of use:

```sh
poetry run python scripts/getting_started_clickhouse.py
```

## Dev setup

Get dependencies

```sh
poetry install
```

Update dev dependencies

```sh
poetry lock
```

Check package (with `ruff` and `mypy`)

```sh
./scripts/check_package.sh
```

Run all pytest tests

```sh
poetry run python -m pytest -vx tests
```

You can run just the tests with `chdb` (for instance if you do not have clickhouse), or just `clickhouse`, by passing the `-m` flag

```sh
poetry run python -m pytest -vxm chdb tests
# or the clickhouse tests:
poetry run python -m pytest -vxm clickhouse tests
```

For clickhouse tests you will need to have docker container running.

Run test scripts

```sh
poetry run python scripts/getting_started_chdb.py
poetry run python scripts/getting_started_clickhouse.py
```

## Known issues

### Datetime parsing

Clickhouse offers several different date formats.
The basic `Date` format cannot handle dates before the epoch (1970-01-01), which makes it unsuitable for many use-cases for holding date-of-births.

The parsing function `parseDateTime` (and variants) which support providing custom formats return a `DateTime`, which also has the above limited range.
In `splinkclickhouse` we use the function `parseDateTime64BestEffortOrNull` so that we can use the extended-range `DateTime64` data type, which supports dates back to 1900-01-01, but does not allow custom date formats. Currently no `DateTime64` equivalent of `parseDateTime` exists.

If you require different behaviour (for instance if you have an unusual date format and know that you do not need dates outside of the `DateTime` range) you will either need to derive a new column manually, or construct the relevant SQL expression manually.

There is not currently a way in Clickhouse to deal directly with date values before 1900 - if you require such values you will have to manually process these to a different type, and construct the relevant SQL logic.

### `NULL` values in `chDB`

When passing data into `chdb` from pandas or pyarrow tables, `NULL` values in `String` columns are converted into empty strings, instead of remaining `NULL`.

For now this is not handled within the package. You can workaround the issue by wrapping column names in `NULLIF`:

```python
import splink.comparison_level as cl

fn_comparison = cl.DamerauLevenshteinAtThresholds("NULLIF(first_name, '')")
```

### Term-frequency adjustments

Currently at most one term frequency adjustment can be used with `ClickhouseAPI`.

This also applies to `ChDBAPI` but _only in `debug_mode`_. With `debug_mode` off there is no limit on term frequency adjustments.
