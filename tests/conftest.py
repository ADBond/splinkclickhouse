import clickhouse_connect
import splink.comparison_library as cl
from chdb import dbapi
from pytest import fixture, mark, param
from splink import ColumnExpression, SettingsCreator, block_on, splink_datasets

from splinkclickhouse import ChDBAPI, ClickhouseAPI

df = splink_datasets.fake_1000


@fixture
def chdb_api():
    con = dbapi.connect()
    yield ChDBAPI(con)
    con.close()


@fixture(scope="module")
def clickhouse_api():
    conn_atts = {
        "host": "localhost",
        "port": 8123,
        "username": "splinkognito",
        "password": "splink123!",
    }

    db_name = "__temp_splink_db_pytest"

    try:
        default_client = clickhouse_connect.get_client(**conn_atts)
        default_client.command(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        client = clickhouse_connect.get_client(
            **conn_atts,
            database=db_name,
        )

        yield ClickhouseAPI(client)
        client.close()
        default_client.command(f"DROP DATABASE {db_name}")
        default_client.close()
    except clickhouse_connect.driver.exceptions.OperationalError:
        yield None


@fixture(
    params=[
        param("chdb", marks=[mark.chdb]),
        param("clickhouse", marks=[mark.clickhouse]),
    ]
)
def api_info(request, chdb_api, clickhouse_api):
    version = request.param
    if version == "chdb":
        return {"db_api": chdb_api, "version": version}
    if version == "clickhouse":
        return {"db_api": clickhouse_api, "version": version}
    raise ValueError(f"Unknown param: {version}")


@fixture(scope="module")
def fake_1000():
    return splink_datasets.fake_1000


@fixture
def fake_1000_settings_factory():
    def fake_1000_settings(version):
        if version == "clickhouse":
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
        # for chdb we wrap all columns in regex_extract, which also includes a nullif
        # this circumvents issue where string column NULL values are parsed as empty
        # string instead of NULL when we import them into chdb
        return SettingsCreator(
            link_type="dedupe_only",
            comparisons=[
                cl.JaroWinklerAtThresholds(
                    ColumnExpression("first_name").regex_extract(".*")
                ),
                cl.JaroAtThresholds(ColumnExpression("surname").regex_extract(".*")),
                cl.DateOfBirthComparison(
                    ColumnExpression("dob").regex_extract(".*"),
                    input_is_string=True,
                ),
                cl.DamerauLevenshteinAtThresholds(
                    ColumnExpression("city").regex_extract(".*")
                ).configure(term_frequency_adjustments=True),
                cl.JaccardAtThresholds(ColumnExpression("email").regex_extract(".*")),
            ],
            blocking_rules_to_generate_predictions=[
                block_on("first_name", "dob"),
                block_on("surname"),
            ],
        )

    return fake_1000_settings
