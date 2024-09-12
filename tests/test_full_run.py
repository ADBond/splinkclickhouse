from splink import Linker, block_on


# this tests similar steps to test_basic_functionality.py, but alltogether
# this should catch issues we may have in building up cache/other state
def test_full_basic_run(api_info, fake_1000_factory, fake_1000_settings):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])
    linker = Linker(df, fake_1000_settings, db_api)

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
