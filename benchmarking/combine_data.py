import json
import os

records = []
for _root, _dirs, files in os.walk("benchmarking/output"):
    for file in files:
        if file.split(".")[1] != "json":
            continue
        if file[0:3] != "run":
            continue
        with open(f"{_root}/{file}", "r") as f:
            records += json.load(f)

with open("benchmarking/output/combined_run_data.json", "w+") as f:
    json.dump(records, f, indent=4)
