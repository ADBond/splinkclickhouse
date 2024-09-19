# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## Added

- Extended `ClickhouseAPI` pandas table registration to support float columns [#24](https://github.com/ADBond/splinkclickhouse/pull/24)
- Added Clickhouse-specific library comparisons/levels - `cll_ch.DistanceInKMLevel`, `cl_ch.DistanceInKMAtThresholds`, and `cl_ch.ExactMatchAtSubstringSizes` [#24](https://github.com/ADBond/splinkclickhouse/pull/24)

## [0.2.3] - 2024-09-16

### Changed

- Dropped support for python 3.8 [#20](https://github.com/ADBond/splinkclickhouse/pull/20)
- Removed `numpy`requirements [#20](https://github.com/ADBond/splinkclickhouse/pull/20)

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

[unreleased]: https://github.com/ADBond/splinkclickhouse/compare/v0.2.3...HEAD
[0.2.3]: https://github.com/ADBond/splinkclickhouse/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/ADBond/splinkclickhouse/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/ADBond/splinkclickhouse/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/ADBond/splinkclickhouse/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/ADBond/splinkclickhouse/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ADBond/splinkclickhouse/releases/tag/v0.1.0
