#!/bin/bash/

uv run python -m pytest -v --cov=splinkclickhouse --cov-branch --cov-report html tests
