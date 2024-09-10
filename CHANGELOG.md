# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [0.1.1] - 2024-09-10

### Fixed

- Fix `random_sample_sql` so that u-training works when we don't sample the entire dataset [#1](https://github.com/ADBond/splinkclickhouse/pull/1)

### Changed

- `try_parse_date` and `try_parse_timestamp` now use `DateTime64` to extend the range to more useful values, and no longer support custom format strings [#2](https://github.com/ADBond/splinkclickhouse/pull/2).

## [0.1.0] - 2024-09-09

### Added

- Basic working version of package

[unreleased]: https://github.com/ADBond/splinkclickhouse/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/ADBond/splinkclickhouse/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ADBond/splinkclickhouse/releases/tag/v0.1.0
