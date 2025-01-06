# Quickstart

## Install

You can install `splinkclickhouse` from [PyPI](https://pypi.org/project/splinkclickhouse/) using `pip`:
```bash
pip install splinkclickhouse
```

or from `conda` on the `conda-forge` channel:
```bash
conda install conda-forge::splinkclickhouse
```

## Run some code

To try out `splinkclickhouse` you can use the following - adjusting the database configuration information to point to your running Clickhouse instance:
```python title="getting_started.py"
import clickhouse_connect
import splink.comparison_library as cl
from splink import Linker, SettingsCreator, block_on, splink_datasets

from splinkclickhouse import ClickhouseServerAPI


client = clickhouse_connect.get_client(
    # adjust as appropriate to point to your clickhouse instance
    host="localhost",
    port=8123,
    username="user",
    password="password",
    database=db_name,
)
# api for Splink to talk to Clickhouse
db_api = ClickhouseServerAPI(client)

# from this point on, all code is standard Splink code,
# not specific to splinkclickhouse

# data, and model settings
df = splink_datasets.fake_1000
settings = SettingsCreator(
    link_type="dedupe_only",
    comparisons=[
        cl.NameComparison("first_name"),
        cl.JaroAtThresholds("surname"),
        cl.DateOfBirthComparison(
            "dob",
            input_is_string=True,
        ),
        cl.DamerauLevenshteinAtThresholds("city").configure(
            term_frequency_adjustments=True
        ),
        cl.EmailComparison("email"),
    ],
    blocking_rules_to_generate_predictions=[
        block_on("first_name", "dob"),
        block_on("surname"),
    ],
)

# set up a linker, train, and get results
linker = Linker(df, settings, db_api)

linker.training.estimate_probability_two_random_records_match(
    [block_on("first_name", "surname")],
    recall=0.7,
)
linker.training.estimate_u_using_random_sampling(max_pairs=1e5)
linker.training.estimate_parameters_using_expectation_maximisation(
    block_on("first_name", "surname")
)
linker.training.estimate_parameters_using_expectation_maximisation(block_on("email"))

pairwise_predictions = linker.inference.predict(threshold_match_weight=-5)

clusters = linker.clustering.cluster_pairwise_predictions_at_threshold(
    pairwise_predictions, 0.95
)

df_clusters = clusters.as_pandas_dataframe()
```
