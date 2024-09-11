from splink import Linker, block_on, splink_datasets


def test_make_linker(db_api, fake_1000_settings):
    df = splink_datasets.fake_1000
    Linker(df, fake_1000_settings, db_api)

def test_train_u(db_api, fake_1000_settings):
    df = splink_datasets.fake_1000
    linker = Linker(df, fake_1000_settings, db_api)
    linker.training.estimate_u_using_random_sampling(max_pairs=3e4)

def test_train_lambda(db_api, fake_1000_settings):
    df = splink_datasets.fake_1000
    linker = Linker(df, fake_1000_settings, db_api)
    linker.training.estimate_probability_two_random_records_match(
        [
            block_on("dob"),
            block_on("first_name", "surname")
        ],
        recall=0.8
    )

def test_em_training(db_api, fake_1000_settings):
    df = splink_datasets.fake_1000
    linker = Linker(df, fake_1000_settings, db_api)
    linker.training.estimate_parameters_using_expectation_maximisation(
        block_on("dob"),
    )
    linker.training.estimate_parameters_using_expectation_maximisation(
        block_on("first_name", "surname"),
    )

def test_predict(db_api, fake_1000_settings):
    df = splink_datasets.fake_1000
    linker = Linker(df, fake_1000_settings, db_api)
    linker.inference.predict()

def test_clustering(db_api, fake_1000_settings):
    df = splink_datasets.fake_1000
    linker = Linker(df, fake_1000_settings, db_api)
    df_predict = linker.inference.predict()
    linker.clustering.cluster_pairwise_predictions_at_threshold(
        df_predict,
        threshold_match_probability=0.8,
    )
