#!/bin/bash
# this is very crude, so take with a large pinch of salt

datasets=("fake_1000" "historical_50k")
backends=("chdb" "duckdb" "clickhouse")

## now loop through the above array
for data_choice in "${datasets[@]}"
do
    for backend in "${backends[@]}"
    do
        echo "Running benchmarks for '$backend' with data: '$data_choice'"
        uv run python benchmarking/benchmark.py $data_choice $backend
    done
done

uv run python benchmarking/combine_data.py
