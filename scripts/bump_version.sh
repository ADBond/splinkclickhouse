#!/bin/bash

set -euo pipefail

echo $1

uv run scripts/update_version.py $1 && uv sync
