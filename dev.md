# Dev guide

## Dev setup

You will need to install [uv](https://docs.astral.sh/uv/).

Install dev dependencies

```sh
uv sync
```

By default these come with the group `chdb` also, but not the `docs` group - to install with these use the `--group` flag.

Manually update dev dependency versions with:

```sh
uv lock
```

Check package (with `ruff` and `mypy`):

```sh
./scripts/check_package.sh
```

### Testing

Run all pytest tests:

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
mkdir -p tmp && tar -xzvf dist/splinkclickhouse-0.4.1.tar.gz -C tmp/
```
