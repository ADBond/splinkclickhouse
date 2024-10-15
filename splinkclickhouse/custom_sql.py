# date parts as integers from date in iso-8601
year = "toInt16OrZero(substring({date_string}, 1, 4))"
month = "toInt16OrZero(substring({date_string}, 6, 2))"
day = "toInt16OrZero(substring({date_string}, 9, 2))"

one_if_leap_year_else_zero = f"""
CASE
    WHEN ({year} % 4 = 0 AND {year} % 100 <> 0) OR {year} % 400 = 0 THEN 1
    ELSE 0
END
"""

# hard-code some results to cut re-computations
# intDiv(1970, 4) == 492
FLOOR_1970_OVER_4 = 492
# intDiv(1970, 100) == 19
FLOOR_1970_OVER_100 = 19
# intDiv(1970, 400) == 4
FLOOR_1970_OVER_400 = 4

# number of leap years between given year and 1970
# not counting the year itself
leap_years_since_1970 = f"""
    (intDiv({year} - 1, 4) - {FLOOR_1970_OVER_4})
    - (intDiv({year} - 1, 100) - {FLOOR_1970_OVER_100})
    + (intDiv({year} - 1, 400) - {FLOOR_1970_OVER_400})
"""
days_from_epoch_to_start_of_year = f"""
({year} - 1970) * 365 + {leap_years_since_1970}
"""

# cumulative days in non-leap years:
# J: 31
# F: 28 + 31 = 59
# M: 31 + 59 = 90
# A: 30 + 90 = 120
# M: 31 + 120 = 151
# J: 30 + 151 = 181
# J: 31 + 181 = 212
# A: 31 + 212 = 243
# S: 30 + 243 = 273
# O: 31 + 273 = 304
# N: 30 + 304 = 334
# D: 31 + 334 = 365 (which we don't need, but is a good check)
# it's to start of month, so we need cumulative total to month before
days_from_start_of_year_to_start_of_month = f"""
CASE
    WHEN {month} = 1 THEN 0
    WHEN {month} = 2 THEN 31
    WHEN {month} = 3 THEN 59 + {one_if_leap_year_else_zero}
    WHEN {month} = 4 THEN 90 + {one_if_leap_year_else_zero}
    WHEN {month} = 5 THEN 120 + {one_if_leap_year_else_zero}
    WHEN {month} = 6 THEN 151 + {one_if_leap_year_else_zero}
    WHEN {month} = 7 THEN 181 + {one_if_leap_year_else_zero}
    WHEN {month} = 8 THEN 212 + {one_if_leap_year_else_zero}
    WHEN {month} = 9 THEN 243 + {one_if_leap_year_else_zero}
    WHEN {month} = 10 THEN 273 + {one_if_leap_year_else_zero}
    WHEN {month} = 11 THEN 304 + {one_if_leap_year_else_zero}
    WHEN {month} = 12 THEN 334 + {one_if_leap_year_else_zero}
END
"""
days_since_start_of_month = f"{day} - 1"

days_since_epoch_sql = f"""
{days_from_epoch_to_start_of_year}
    + {days_from_start_of_year_to_start_of_month}
    + {days_since_start_of_month}
""".format(date_string="date_string")
