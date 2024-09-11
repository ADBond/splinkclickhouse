import clickhouse_connect
import splink.comparison_library as cl
from chdb import dbapi
from pytest import fixture
from splink import SettingsCreator, block_on, splink_datasets

from splinkclickhouse import ChDBAPI, ClickhouseAPI

df = splink_datasets.fake_1000


@fixture
def chdb_api():
    con = dbapi.connect()
    yield ChDBAPI(con)
    con.close()

@fixture(scope="module")
def clickhouse_api(_fake_1000):
    conn_atts = {
        "host": "localhost",
        "port": 8123,
        "username": "splinkognito",
        "password": "splink123!",
    }

    db_name = "__temp_splink_db_pytest"
    tn = "fake_1000"

    default_client = clickhouse_connect.get_client(**conn_atts)
    default_client.command(
        f"CREATE DATABASE IF NOT EXISTS {db_name}"
    )
    client = clickhouse_connect.get_client(
        **conn_atts,
        database=db_name,
    )
    client.command(
        f"CREATE OR REPLACE TABLE {tn} "
        "(unique_id UInt32, first_name Nullable(String), surname Nullable(String), "
        "dob Nullable(String), city Nullable(String), email Nullable(String), "
        "cluster UInt8) "
        "ENGINE MergeTree "
        "ORDER BY unique_id"
    )
    client.insert_df(tn, _fake_1000)

    yield ClickhouseAPI(client)
    client.close()
    default_client.command(
        f"DROP DATABASE {db_name}"
    )
    default_client.close()

@fixture(params=["chdb", "clickhouse"])
def api_info(request, chdb_api, clickhouse_api):
    version = request.param
    if version == "chdb":
        return {"db_api": chdb_api, "version": version}
    if version == "clickhouse":
        return {"db_api": clickhouse_api, "version": version}
    raise ValueError(f"Unknown param: {version}")

@fixture(scope="module")
def _fake_1000():
    return splink_datasets.fake_1000

@fixture
def fake_1000_factory(_fake_1000):
    def fake_1000(version):
        if version == "chdb":
            return _fake_1000
        return "fake_1000"
    return fake_1000

@fixture
def fake_1000_settings():
    return SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.JaroWinklerAtThresholds("first_name"),
            cl.JaroAtThresholds("surname"),
            cl.DateOfBirthComparison(
                "dob",
                input_is_string=True,
            ),
            cl.DamerauLevenshteinAtThresholds("city").configure(
                term_frequency_adjustments=True
            ),
            cl.JaccardAtThresholds("email"),
        ],
        blocking_rules_to_generate_predictions=[
            block_on("first_name", "dob"),
            block_on("surname"),
        ],
    )
