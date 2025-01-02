import numpy as np
import pandas as pd
import splink.comparison_library as cl
from splink import Linker, SettingsCreator


def test_register_pandas_types(api_info, fake_1000, fake_1000_settings_factory):
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
    settings = SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.ExactMatch("name"),
        ],
    )
    Linker(df, settings, db_api)
