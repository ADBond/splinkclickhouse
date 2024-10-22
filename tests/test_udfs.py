from pytest import mark

# datestrings, and the number of days difference to 1970-01-01
test_data = [
    ("1970-01-01", 0),
    ("1969-12-31", -1),
    ("1970-01-02", 1),
    ("1970-10-31", 303),
    # check leap years before and after, and before and after leap day
    ("1968-01-01", -731),
    ("1968-03-01", -671),
    ("1972-02-01", 761),
    ("1972-05-01", 851),
    # check some dates around and beyond millenium
    ("1999-12-31", 10_956),
    ("2000-01-01", 10_957),
    ("2000-06-03", 11_111),
    ("2024-10-19", 20_015),
    ("2307-02-07", 123_123),
    # and check some before 1900 (not leap year), and before 1600 (was)
    ("1783-03-18", -68_224),
    ("1761-04-07", -76_239),
    ("1533-09-07", -159_362),
]


# should be same between chdb + clickhouse server, but can't hurt to check both
@mark.parametrize(("date_string", "expected_result"), test_data)
def test_days_since_epoch(api_info, date_string, expected_result):
    db_api = api_info["db_api_factory"]()

    sql = f"SELECT days_since_epoch('{date_string}') AS days_difference"

    res_df = db_api.sql_to_splink_dataframe_checking_cache(
        sql,
        "test_dse_table",
        use_cache=False,
    )
    res_list = res_df.as_record_dict()
    assert len(res_list) == 1
    assert res_list[0]["days_difference"] == expected_result
