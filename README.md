[![pypi](https://img.shields.io/github/v/release/adbond/splinkclickhouse?include_prereleases)](https://pypi.org/project/splinkclickhouse/#history)
[![Downloads](https://static.pepy.tech/badge/splinkclickhouse)](https://pepy.tech/project/splinkclickhouse)
[![codecov](https://codecov.io/github/adbond/splinkclickhouse/graph/badge.svg?token=NUHM8IPJL4)](https://codecov.io/github/adbond/splinkclickhouse)
[![Docs](https://img.shields.io/badge/documentation-purple?style=flat)](https://adbond.github.io/splinkclickhouse/)

# `splinkclickhouse`

Basic [Clickhouse](https://clickhouse.com/docs/en/intro) support for use as a backend with the data-linkage and deduplication package [Splink](https://moj-analytical-services.github.io/splink/).

Supports clickhouse server connected via [clickhouse connect](https://clickhouse.com/docs/en/integrations/python).

Also supports in-process [chDB](https://clickhouse.com/docs/en/chdb) version if installed with the `chdb` extras.

## Installation

Install from `PyPI` using `pip`:

```sh
# just installs the Clickhouse server dependencies
pip install splinkclickhouse
# or to install with support for chdb:
pip install splinkclickhouse[chdb]
```

or you can install the package directly from github:

```sh
# Replace with any version you want, or specify a branch after '@'
pip install git+https://github.com/ADBond/splinkclickhouse.git@v0.4.1
```

If instead you are using `conda`, `splinkclickhouse` is available on [conda-forge](https://conda-forge.org/):

```sh
conda install conda-forge::splinkclickhouse
```

Note that the `conda` version will only be able to use [the Clickhouse server functionality](#clickhouse-server) as `chdb` is not currently available within `conda`.

## Documentation

Head over to [the docs site](https://adbond.github.io/splinkclickhouse/) for details on using the package. 

### Caveats

While the package is in early development there will may be breaking changes in new versions without warning, although these _should_ only occur in new minor versions.
Nevertheless if you depend on this package it is recommended to pin a version to avoid any disruption that this may cause.

It is tested against Clickhouse server version 24.8.
There have also been occasional tests against 24.11.
Other versions are likely to function normally, but if you have a significantly different version, functionality may be affected.

### Dev setup

For dev setup see [dev.md](./dev.md).

## Support

If you have difficulties with the package you can [open an issue](https://github.com/ADBond/splinkclickhouse/issues).
You may also [suggest changes by opening a PR](https://github.com/ADBond/splinkclickhouse/pulls), although it may be best to discuss in an issue beforehand.

This package is 'unofficial', in that it is not directly supported by the Splink team. Maintenance / improvements will be done on a 'best effort' basis where resources allow.
