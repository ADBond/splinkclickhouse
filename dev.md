# Dev guide

## Using

### ChDB

Import the relevant api:

```python
from splinkclickhouse import ChDBAPI
```

See [getting started script](./scripts/getting_started_chdb.py) for example of use:

```sh
uv run python scripts/getting_started_chdb.py
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
uv run python scripts/getting_started_clickhouse.py
```

## Dev setup

Get dependencies

```sh
uv sync
```

Update dev dependencies (although this happens automatically)

```sh
uv lock
```

Check package (with `ruff` and `mypy`)

```sh
./scripts/check_package.sh
```

Run all pytest tests

```sh
uv run python -m pytest -vx tests
```

You can run just the tests with `chdb` (for instance if you do not have clickhouse), or just `clickhouse`, by passing the `-m` flag

```sh
uv run python -m pytest -vxm chdb tests
# or the clickhouse tests:
uv run python -m pytest -vxm clickhouse tests
```

For clickhouse tests you will need to have docker container running.

Run test scripts

```sh
uv run python scripts/getting_started_chdb.py
uv run python scripts/getting_started_clickhouse.py
```

## Bump package version

From root of repo:

```sh
./scripts/bump_version.sh X.X.X
```

## Build

Build package to `dist/`

```sh
uv build --package splinkclickhouse
```

Inspect package contents:

```sh
# replace version as appropriate
mkdir -p tmp && tar -xzvf dist/splinkclickhouse-0.2.3.tar.gz -C tmp/
```

### Manual publish

Set `TWINE_PASSWORD` as an appropriate API token. This is to TestPyPI - remove option for the real thing.

```sh
TWINE_USERNAME=__token__ uvx twine upload -r testpypi dist/*
```

See [twine docs](https://twine.readthedocs.io/en/stable/) for more info.
