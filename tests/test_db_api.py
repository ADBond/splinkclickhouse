import numpy as np
import pandas as pd
from pytest import raises


def test_register_pandas_types(api_info):
    db_api = api_info["db_api_factory"]()
    df = pd.DataFrame(
        {
            "unique_id": pd.to_numeric([1, 2, 3], downcast="unsigned"),
            "name": ["a", "b", "c"],
            "aliases": [["A", "aa"], [], ["Cc", "ccc", "cCc"]],
            "height": [10.2, 11.3, 8.2],
            "dob": [
                np.datetime64("1984-05-15"),
                np.datetime64("1983-10-30"),
                np.datetime64("1992-02-17"),
            ],
            "date_int": [-1_242, 765, 3_912],
        }
    )
    db_api.register_table(df, "my_pandas_input_table")


def test_register_records_list(api_info):
    db_api = api_info["db_api_factory"]()

    records_list = [
        {"id": 1, "name": "one"},
        {"id": 2, "name": "two"},
        {"id": 3, "name": "three"},
    ]

    db_api.register_table(records_list, "my_list_input_table")


def test_register_data_dict(api_info):
    db_api = api_info["db_api_factory"]()

    records_dict = {
        "id": [1, 2, 3],
        "name": ["a", "b", "c"],
    }

    db_api.register_table(records_dict, "my_dict_input_table")


def test_nice_error_bad_register_type(api_info):
    db_api = api_info["db_api_factory"]()
    with raises(TypeError):
        db_api.register_table(3, "the_number_three")
