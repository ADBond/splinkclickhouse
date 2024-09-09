# `splinkclickhouse`

Basic [Clickhouse](https://clickhouse.com/docs/en/intro) support for use as a backend with the data-linkage and deduplication package [Splink](https://moj-analytical-services.github.io/splink/).

Currently only support for in-process [chDB](https://clickhouse.com/docs/en/chdb) version.

## Using

```sh
poetry run python scripts/getting_started.py
```

See [getting started script](./scripts/getting_started.py) for example of use.

## Dev setup

Get dependencies

```sh
poetry install
```

Update dev dependencies

```sh
poetry lock
```

Check package

```sh
./scripts/check_package.sh
```

Run test script

```sh
poetry run python scripts/getting_started.py
```
