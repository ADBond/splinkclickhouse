# Splinkclickhouse libraries

Splink models work by specifying what types of comparisons between pairs of records will be taken into account, as described in [this Splink user guide on comparisons](https://moj-analytical-services.github.io/splink/topic_guides/comparisons/comparisons_and_comparison_levels.html).

Splink provides several premade tools for common use-cases in the [comparison library](https://moj-analytical-services.github.io/splink/api_docs/comparison_library.html) and [comparison level library](https://moj-analytical-services.github.io/splink/api_docs/comparison_level_library.html).

Most of these will work out-of-the-box with `splinkclickhouse` - simply use them in the same way described in the Splink documentation by importing:

```python
import splink.comparison_library as cl
import splink.comparison_level_library as cll
```

However, `splinkclickhouse` also extends and supplements these for a few potential use-cases.

## Custom libraries

The `splinkclickhouse` libraries are used in exactly the same way as the Splink libraries.
We generally recommend using a different alias for them to improve code clarity, especially as some have the same name as Splink versions:
```python
import splinkclickhouse.comparison_library as cl_ch
import splinkclickhouse.comparison_level_library as cll_ch
```

Use just as in Splink - either pre-made comparisons:
```python
import splink.comparison_library as cl
from splink import SettingsCreator

import splinkclickhouse.comparison_library as cl_ch

...
settings = SettingsCreator(
    link_type="dedupe_only",
    comparisons=[
        cl.ExactMatch("name"),
        cl_ch.DistanceInKMAtThresholds(
            "latitude",
            "longitude",
            [10, 50, 100, 200, 500],
        ),
    ],
)
```

or customise individual levels to construct custom comparisons:

```python
import splink.comparison_level_library as cll
import splink.comparison_library as cl
from splink import SettingsCreator

import splinkclickhouse.comparison_level_library as cll_ch

...
settings = SettingsCreator(
    link_type="dedupe_only",
    comparisons=[
        cl.ExactMatch("name"),
        cl.CustomComparison(
            comparison_levels = [
                cll.And(
                    cll.NullLevel("city"),
                    cll.NullLevel("postcode"),
                    cll.Or(cll.NullLevel("latitude"), cll.NullLevel("longitude"))
                ),
                cll.ExactMatch("postcode"),
                cll_ch.DistanceInKMLevel("latitude", "longitude", 5),
                cll_ch.DistanceInKMLevel("latitude", "longitude", 10),
                cll.ExactMatch("city"),
                cll_ch.DistanceInKMLevel("latitude", "longitude", 50),
                cll.ElseLevel(),
            ],
            output_column_name="location",
        ),
    ],
)
```

## `splinkclickhouse.comparison_level_library`

The following Clickhouse-specific comparisons are available in the `splinkclickhouse` comparison level library.

All others can be found in the ordinary Splink comparison level library.

::: splinkclickhouse.comparison_level_library

## `splinkclickhouse.comparison_library`

The following Clickhouse-specific comparisons are available in the `splinkclickhouse` comparison library.

All others can be found in the ordinary Splink comparison library.

::: splinkclickhouse.comparison_library
