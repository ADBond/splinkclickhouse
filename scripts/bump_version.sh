#!/bin/bash

set -euo pipefail

echo Updating files for version: $1

uv run scripts/update_version.py $1
uv sync --group docs

echo Done!
