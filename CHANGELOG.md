# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Renamed `ClickhouseAPI` and `ClickhouseDataFrame` to `ClickhouseServerAPI` and `ClickhouseServerDataFrame` respectively, and `splinkclickhouse.clickhouse` to `splinkclickhouse.clickhouse_server` [#54](https://github.com/ADBond/splinkclickhouse/pull/54).

## [0.3.4] - 2024-12-16

### Added

- Added Clickhouse appropriate versions of comparison level `PairwiseStringDistanceFunctionLevel` and comparison `PairwiseStringDistanceFunctionAtThresholds` to the relevant libraries [#51](https://github.com/ADBond/splinkclickhouse/pull/51).
- `ClickhouseAPI` can now properly register `pandas` tables with string array columns [#51](https://github.com/ADBond/splinkclickhouse/pull/51).

### Fixed

- Table registration in `chdb` now works for pandas tables whose indexes do not have a `0` entry [#49](https://github.com/ADBond/splinkclickhouse/pull/49).

## [0.3.3] - 2024-12-05

### Added

- Term frequency adjustments are now not limited in Clickhouse server (or `chdb` when `debug_mode` is switched on) [#46](https://github.com/ADBond/splinkclickhouse/pull/46).

### Changed

- Dropped support for Splink <= `4.0.5` [#46](https://github.com/ADBond/splinkclickhouse/pull/46).

## [0.3.2] - 2024-10-23

### Added

- SQL UDF `days_since_epoch` to parse a date representing a string to the number of days since `1970-01-01` [#39](https://github.com/ADBond/splinkclickhouse/pull/39).
- Custom Clickhouse `ColumnExpression` with additional transform `parse_date_to_int` to parse string to days since epoch [#39](https://github.com/ADBond/splinkclickhouse/pull/39).
- Custom date comparison and comparison levels working with integer type representing days since epoch [#39](https://github.com/ADBond/splinkclickhouse/pull/39).

## [0.3.1] - 2024-10-14

### Added

- `ClickhouseAPI` now has a function `.set_union_default_mode()` to allow manually setting client state necessary for clustering, if session has timed out e.g. when running interactively [#36](https://github.com/ADBond/splinkclickhouse/pull/36).
- Added support for Splink 4.0.4 [#37](https://github.com/ADBond/splinkclickhouse/pull/37).

### Fixed

- `estimate_probability_two_random_records_match` now works correctly when `debug_mode` is switched on [#34](https://github.com/ADBond/splinkclickhouse/pull/34).

## [0.3.0] - 2024-09-26

### Changed

- `chdb` is now an optional dependency, requiring opt-in installation for use of `ChDBAPI` [#28](https://github.com/ADBond/splinkclickhouse/pull/28).

## [0.2.5] - 2024-09-23

### Changed

- Added support for Splink >= 4.0.2, dropped support for 4.0.0, 4.0.1 [#26](https://github.com/ADBond/splinkclickhouse/pull/26).

## [0.2.4] - 2024-09-19

## Added

- Extended `ClickhouseAPI` pandas table registration to support float columns [#24](https://github.com/ADBond/splinkclickhouse/pull/24).
- Added Clickhouse-specific library comparisons/levels - `cll_ch.DistanceInKMLevel`, `cl_ch.DistanceInKMAtThresholds`, and `cl_ch.ExactMatchAtSubstringSizes` [#24](https://github.com/ADBond/splinkclickhouse/pull/24).

## [0.2.3] - 2024-09-16

### Changed

- Dropped support for python 3.8 [#20](https://github.com/ADBond/splinkclickhouse/pull/20).
- Removed `numpy`requirements [#20](https://github.com/ADBond/splinkclickhouse/pull/20).

## [0.2.2] - 2024-09-12

### Added

- `ClickhouseAPI` now allows for registering tables directly from pandas `DataFrame`s, if they contain only integer and string columns [#18](https://github.com/ADBond/splinkclickhouse/pull/18).

### Fixed

- Create an alias for `rand`, `random` so that `Linker.visualisations.comparison_viewer_dashboard` runs without error [#14](https://github.com/ADBond/splinkclickhouse/pull/14).
- Workaround for Clickhouse `count(*) filter ...` parsing issue so that `linker.clustering.compute_graph_metrics(...)` now runs [#18](https://github.com/ADBond/splinkclickhouse/pull/18).

## [0.2.1] - 2024-09-12

### Changed

- Updated `numpy` dependency requirements to allow compatible versions for all supported python versions [#9](https://github.com/ADBond/splinkclickhouse/pull/9).

## [0.2.0] - 2024-09-11

### Added

- `ClickhouseAPI` and dataframe added to support running calculations in a Clickhouse instance [#4](https://github.com/ADBond/splinkclickhouse/pull/4).

## [0.1.1] - 2024-09-10

### Fixed

- Fix `random_sample_sql` so that u-training works when we don't sample the entire dataset [#1](https://github.com/ADBond/splinkclickhouse/pull/1).

### Changed

- `try_parse_date` and `try_parse_timestamp` now use `DateTime64` to extend the range to more useful values, and no longer support custom format strings [#2](https://github.com/ADBond/splinkclickhouse/pull/2).

## [0.1.0] - 2024-09-09

### Added

- Basic working version of package with api for `chdb`

[Unreleased]: https://github.com/ADBond/splinkclickhouse/compare/v0.3.4...HEAD
[0.3.4]: https://github.com/ADBond/splinkclickhouse/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/ADBond/splinkclickhouse/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/ADBond/splinkclickhouse/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/ADBond/splinkclickhouse/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/ADBond/splinkclickhouse/compare/v0.2.5...v0.3.0
[0.2.5]: https://github.com/ADBond/splinkclickhouse/compare/v0.2.4...v0.2.5
[0.2.4]: https://github.com/ADBond/splinkclickhouse/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/ADBond/splinkclickhouse/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/ADBond/splinkclickhouse/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/ADBond/splinkclickhouse/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/ADBond/splinkclickhouse/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/ADBond/splinkclickhouse/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ADBond/splinkclickhouse/releases/tag/v0.1.0
