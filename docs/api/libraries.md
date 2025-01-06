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

## `splinkclickhouse.comparison_library`

The following Clickhouse-specific comparisons are available in the `splinkclickhouse` comparison library.

All others can be found in the ordinary Splink comparison library.

::: splinkclickhouse.comparison_library


## `splinkclickhouse.comparison_level_library`

The following Clickhouse-specific comparisons are available in the `splinkclickhouse` comparison level library.

All others can be found in the ordinary Splink comparison level library.

::: splinkclickhouse.comparison_level_library