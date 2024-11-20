import json
import os
from copy import deepcopy

import altair as alt

records = []
for _root, _dirs, files in os.walk("benchmarking/output"):
    for file in files:
        if file.split(".")[1] != "json":
            continue
        if file[0:3] != "run":
            continue
        print(f"Adding records from file {file}")  # noqa: T201
        with open(f"{_root}/{file}", "r") as f:
            records += json.load(f)

print(f"All run data: {records}")  # noqa: T201
with open("benchmarking/output/combined_run_data.json", "w+") as f:
    json.dump(records, f, indent=4)

with open("benchmarking/utils/stacked_bar_spec.json", "r") as f:
    graph_dict = json.load(f)

graph_dict["data"]["values"] = records

for data_choice in ("fake_1000", "historical_50k"):
    data_graph_dict = deepcopy(graph_dict)
    data_graph_dict["transform"][0]["filter"] = graph_dict["transform"][0][
        "filter"
    ].replace("__data_choice__", data_choice)

    chart = alt.Chart.from_dict(data_graph_dict)
    chart.save(f"benchmarking/output/chart_{data_choice}.html")
