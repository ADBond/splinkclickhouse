# perhaps some overlap with other tests
# but these are specifically focussing on debug_mode
# don't want to confuse 'normal' functionality tests with these

# we run versions with debug on AND OFF so we make sure that errors
# occur only in debug_mode=True version. Probably a neater way to package that,
# but this will do for now
from pytest import mark
from splink import Linker, block_on


# all-in-one workflow
@mark.parametrize("debug_mode", [False, True])
def test_full_basic_run(api_info, fake_1000, fake_1000_settings_factory, debug_mode):
    db_api = api_info["db_api"]
    df = fake_1000
    fake_1000_settings = fake_1000_settings_factory(api_info["version"])
    linker = Linker(df, fake_1000_settings, db_api)
    db_api.debug_mode = debug_mode

    # training
    linker.training.estimate_u_using_random_sampling(max_pairs=6e5)
    linker.training.estimate_probability_two_random_records_match(
        [block_on("dob"), block_on("first_name", "surname")], recall=0.8
    )
    linker.training.estimate_parameters_using_expectation_maximisation(
        block_on("dob"),
    )
    linker.training.estimate_parameters_using_expectation_maximisation(
        block_on("first_name", "surname"),
    )

    # predict
    df_predict = linker.inference.predict()
    # and cluster
    linker.clustering.cluster_pairwise_predictions_at_threshold(
        df_predict,
        threshold_match_probability=0.9,
    )
