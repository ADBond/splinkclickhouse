#!/bin/bash

set -euo pipefail

uv run python -m ruff check splinkclickhouse && uv run python -m ruff format splinkclickhouse
uv run python -m mypy splinkclickhouse

uv run python -m ruff check tests && uv run python -m ruff format tests
