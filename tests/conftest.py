import splink.comparison_library as cl
from chdb import dbapi
from pytest import fixture
from splink import SettingsCreator, block_on

from splinkclickhouse import ChDBAPI


@fixture
def chdb_api():
    con = dbapi.connect()
    yield ChDBAPI(con)
    con.close()

@fixture(params=["chdb"])
def db_api(request, chdb_api):
    version = request.param
    if version == "chdb":
        return chdb_api

@fixture
def fake_1000_settings():
    return SettingsCreator(
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
