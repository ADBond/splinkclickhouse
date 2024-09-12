from splink import Linker, block_on
from splink.blocking_analysis import (
    cumulative_comparisons_to_be_scored_from_blocking_rules_chart,
)
from splink.exploratory import completeness_chart, profile_columns


def test_make_linker(api_info, fake_1000_factory, fake_1000_settings):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])
    Linker(df, fake_1000_settings, db_api)


def test_train_u(api_info, fake_1000_factory, fake_1000_settings):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])
    linker = Linker(df, fake_1000_settings, db_api)
    linker.training.estimate_u_using_random_sampling(max_pairs=3e4)


def test_train_lambda(api_info, fake_1000_factory, fake_1000_settings):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])
    linker = Linker(df, fake_1000_settings, db_api)
    linker.training.estimate_probability_two_random_records_match(
        [block_on("dob"), block_on("first_name", "surname")], recall=0.8
    )


def test_em_training(api_info, fake_1000_factory, fake_1000_settings):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])
    linker = Linker(df, fake_1000_settings, db_api)
    linker.training.estimate_parameters_using_expectation_maximisation(
        block_on("dob"),
    )
    linker.training.estimate_parameters_using_expectation_maximisation(
        block_on("first_name", "surname"),
    )


def test_predict(api_info, fake_1000_factory, fake_1000_settings):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])
    linker = Linker(df, fake_1000_settings, db_api)
    linker.inference.predict()


def test_clustering(api_info, fake_1000_factory, fake_1000_settings):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])
    linker = Linker(df, fake_1000_settings, db_api)
    df_predict = linker.inference.predict()
    linker.clustering.cluster_pairwise_predictions_at_threshold(
        df_predict,
        threshold_match_probability=0.8,
    )


def test_cumulative_comparisons(api_info, fake_1000_factory, fake_1000_settings):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])

    blocking_rules = fake_1000_settings.blocking_rules_to_generate_predictions

    cumulative_comparisons_to_be_scored_from_blocking_rules_chart(
        table_or_tables=df,
        blocking_rules=blocking_rules,
        db_api=db_api,
        link_type="dedupe_only",
    )


def test_profiling(api_info, fake_1000_factory):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])

    profile_columns(
        df,
        db_api=db_api,
        column_expressions=["first_name", "surname", "city", "first_name || surname"],
    )


def test_completeness(api_info, fake_1000_factory):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])

    completeness_chart(df, db_api=db_api)


def test_match_weights_chart(api_info, fake_1000_factory, fake_1000_settings):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])
    linker = Linker(df, fake_1000_settings, db_api)
    linker.visualisations.match_weights_chart()


def test_parameter_estimates_chart(api_info, fake_1000_factory, fake_1000_settings):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])
    linker = Linker(df, fake_1000_settings, db_api)
    linker.training.estimate_parameters_using_expectation_maximisation(
        block_on("dob"),
    )
    linker.training.estimate_parameters_using_expectation_maximisation(
        block_on("first_name", "surname"),
    )
    linker.visualisations.parameter_estimate_comparisons_chart()


def test_m_u_chart(api_info, fake_1000_factory, fake_1000_settings):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])
    linker = Linker(df, fake_1000_settings, db_api)

    linker.visualisations.m_u_parameters_chart()


def test_unlinkables_chart(api_info, fake_1000_factory, fake_1000_settings):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])
    linker = Linker(df, fake_1000_settings, db_api)

    linker.evaluation.unlinkables_chart()


def test_comparison_viewer_dashboard(
    api_info, fake_1000_factory, fake_1000_settings, tmp_path
):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])
    fake_1000_settings.retain_intermediate_calculation_columns = True
    linker = Linker(df, fake_1000_settings, db_api)

    df_predict = linker.inference.predict()
    linker.visualisations.comparison_viewer_dashboard(df_predict, tmp_path / "cvd.html")


def test_cluster_studio_dashboard(
    api_info, fake_1000_factory, fake_1000_settings, tmp_path
):
    db_api = api_info["db_api"]
    df = fake_1000_factory(api_info["version"])
    fake_1000_settings.retain_intermediate_calculation_columns = True
    linker = Linker(df, fake_1000_settings, db_api)

    df_predict = linker.inference.predict()
    df_clustered = linker.clustering.cluster_pairwise_predictions_at_threshold(
        df_predict,
        threshold_match_probability=0.8,
    )
    linker.visualisations.cluster_studio_dashboard(
        df_predict, df_clustered, tmp_path / "csd.html"
    )
