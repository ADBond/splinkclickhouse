#!/bin/bash

set -euo pipefail

poetry run ruff check splinkclickhouse && poetry run ruff format splinkclickhouse
poetry run mypy splinkclickhouse

poetry run ruff check tests && poetry run ruff format tests
