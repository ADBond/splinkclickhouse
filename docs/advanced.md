# Advanced usage

Here are a few topics that are probably less relevant for typical users, but may be required for specialist use-cases.

## Working with dates

If you already have dates in your tables with an appropriate type you probably needn't read any further - you can just work as usual with these columns, using Splink library functions [AbsoluteTimeDifferenceAtThresholds](https://moj-analytical-services.github.io/splink/api_docs/comparison_library.html#splink.comparison_library.AbsoluteTimeDifferenceAtThresholds), [DateOfBirthComparison](https://moj-analytical-services.github.io/splink/api_docs/comparison_library.html#splink.comparison_library.DateOfBirthComparison), [AbsoluteTimeDifferenceLevel](https://moj-analytical-services.github.io/splink/api_docs/comparison_level_library.html#splink.comparison_level_library.AbsoluteTimeDifferenceLevel), or writing custom SQL with [CustomLevel](https://moj-analytical-services.github.io/splink/api_docs/comparison_level_library.html#splink.comparison_level_library.CustomLevel) and [CustomComparison](https://moj-analytical-services.github.io/splink/api_docs/comparison_library.html#splink.comparison_library.CustomComparison).

However if you have _unprocessed_ dates - either `String` columns in Clickhouse, or data that you haven't imported into Clickhouse yet, there are a couple of things to be aware of.

### Types

If you have dates in strings (for instance if you want to preserve typos which may be invalid dates, but still compare to other dates), Splink can convert during the matching process to a suitable date type using [a suitable type conversion function](https://clickhouse.com/docs/en/sql-reference/functions/type-conversion-functions).

Ideally this will be done beforehand to derive a new column with the converted type. This will usually be more performant as you only need to do it once per input record, although it does mean you will need to store an extra column of data for each date.

#### DateTime64

If you use built-in Splink functions (rather than writing custom SQL) this will use the largest type [DateTime64](https://clickhouse.com/docs/en/sql-reference/data-types/datetime64) via the function [parseDateTime64BestEffortOrNull](https://clickhouse.com/docs/en/sql-reference/functions/type-conversion-functions#parsedatetime64besteffortornull). This function is chosen as:

* the 32-bit [`DateTime`](https://clickhouse.com/docs/en/sql-reference/data-types/datetime) type only goes back to 1970 so is unsuitable for many use-cases (where dates-of-birth are commonly used)
* in most cases we wish for invalid dates to evaluate to `NULL` for this purpose, and this is the only way to do so with `DateTime64` - there is no comparable function where you can specify arbitrary formats

If you wish to use a different date type, or wish to specify a particular format you will need to write your own SQL and wrap in the appropriate conversion function.

#### Integer dates

`DateTime64` is _also_ limited in range, not supporting dates prior to the beginning of 1900.
You may, however, be interested in working with such dates in linkage jobs, such as linking historical data.

`splinkclickhouse` comes with some tools to aid with such dates. There is some custom SQL that converts such dates (expressed as ISO-8601 strings) into a signed integer (the number of days since the Unix epoch '1970-01-01', using the [proleptic Gregorian calendar](https://en.wikipedia.org/wiki/Proleptic_Gregorian_calendar)). When you create a `ClickhouseServerAPI` or `ChDBAPI` this function will be refistered as a UDF `days_since_epoch`.

The[`splinkclickhouse` custom library functions](./api/libraries.md) pertaining to dates if compose the logic for interpreting these integers back as dates to compute time intervals for you. They work either with a pre-processed integer column, or with a string column (which will then use `days_since_epoch` under-the-hood).

You can also use the function `days_since_epoch` in custom SQL, or use the [`ColumnExpression`](#columnexpression) method `parse_date_to_int`.

## `ColumnExpression`

## `ClickhouseDialect`
