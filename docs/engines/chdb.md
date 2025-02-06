# chdb

`splinkclickhouse` can be used with [the in-process enginge chdb](https://github.com/chdb-io/chdb).

## Installation

You will need to have `chdb` installed. This is not provided by default, but comes if you request the 'chdb' extras:

```bash
pip install "splinkclickhouse[chdb]"
```

Alternatively you can manually install `chdb` after-the-fact.

`chdb` is not currently available in `conda`.

## Known issues

### `NULL` values

When passing data into `chdb` from pandas or pyarrow tables, `NULL` values in `String` columns are converted into empty strings, instead of remaining `NULL`.

For now this is not handled within the package. You can workaround the issue by wrapping column names in `NULLIF`:
```python
import splink.comparison_level as cl

first_name_comparison = cl.DamerauLevenshteinAtThresholds("NULLIF(first_name, '')")
```
