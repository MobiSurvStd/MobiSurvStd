from dataclasses import dataclass

import polars as pl

from mobisurvstd.resources.nuts import NUTS_DF

# Regular expression to match INSEE municipality codes.
INSEE_REGEX = "^[0-9][0-9AB][0-9][0-9][0-9]$"


class GuaranteeResult:
    @classmethod
    def from_bool(cls, value: bool) -> "GuaranteeResult":
        return Valid() if value else Invalid()


@dataclass
class Valid(GuaranteeResult):
    """The guarantee is valid."""

    pass


@dataclass
class Invalid(GuaranteeResult):
    """The guarantee is not valid."""

    pass


@dataclass
class AutoFixed(GuaranteeResult):
    """The guarantee is valid after auto-fixing the DataFrame."""

    df: pl.DataFrame


def polars_expr_to_string(expr: pl.Expr):
    s = str(expr)
    for char in ("col(", "(", ")", "[", "]"):
        s = s.replace(char, "")
    for char in (".",):
        s = s.replace(char, " ")
    s = s.replace("is_in", "is either ")
    s = s.replace("is_not_null", "is not NULL")
    s = s.replace("is_null", "is NULL")
    return s


class Guarantee:
    def __init__(
        self, *, when: pl.Expr | None = None, when_alias: str | None = None, fix_value=None
    ):
        if when_alias is not None:
            assert when is not None
        self.when = when
        self.when_alias = when_alias
        if when_alias is None and when is not None:
            # Automatically create an alias.
            self.when_alias = polars_expr_to_string(when)
        # Value to be used as default when auto-fixing errors. By default, this will be None
        # (=NULL).
        self.fix_value = fix_value

    def check(self, df: pl.DataFrame, col: str) -> bool:
        res = self._check(self.preprocess(df), col)
        return res

    def preprocess(self, df: pl.DataFrame) -> pl.DataFrame:
        if self.when is not None:
            return df.filter(self.when)
        else:
            return df

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        raise NotImplementedError

    def fail_msg(self, df: pl.DataFrame, col: str) -> str:
        msg = self._fail_msg(self.preprocess(df), col)
        if self.when_alias is not None:
            msg += f" when {self.when_alias}"
        return msg

    def auto_fix(self, df: pl.DataFrame, col: str) -> pl.DataFrame | None:
        fix = self._auto_fix(col)
        if fix is None:
            return None
        assert isinstance(fix, pl.Expr)
        if self.when is not None:
            return df.with_columns(pl.when(self.when).then(fix).otherwise(col).alias(col))
        else:
            return df.with_columns(fix.alias(col))

    def _auto_fix(self, col: str) -> pl.Expr | None:
        return None


class MultipleGuarantees(Guarantee):
    """Special guarantee to check multiple guarantees at once."""

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.guarantees = args

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        return all(g.check(df, col) for g in self.guarantees)

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        for g in self.guarantees:
            if not g.check(df, col):
                return g.fail_msg(df, col)
        raise Exception("Unreachable")

    def auto_fix(self, df: pl.DataFrame, col: str) -> pl.DataFrame | None:
        modified = False
        for g in self.guarantees:
            if g.check(df, col):
                # No auto-fix needed.
                continue
            df_or_none = g.auto_fix(df, col)
            if df_or_none is not None:
                modified = True
                df = df_or_none
        if modified:
            return df
        else:
            return None


class Unique(Guarantee):
    """Guarantee for variables whose values are all unique."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        return df[col].n_unique() == len(df)

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        counts = df[col].value_counts(sort=True).filter(pl.col("count") > 1)
        return f"Values are not all unique:\n{counts}"


class Sorted(Guarantee):
    """Guarantee for variables whose values are sorted."""

    def __init__(self, descending: bool = False, over: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.descending = descending
        self.over = over

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        if self.over is None:
            return df[col].is_sorted(descending=self.descending)
        else:
            return df.select(
                (pl.col(col).sort(descending=self.descending).over(self.over) == pl.col(col)).all()
            ).item()

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        if self.over is None:
            diff = df[col].diff()
            if self.descending:
                idx = (diff > 0).arg_max()
            else:
                idx = (diff < 0).arg_max()
            v0 = df[col][idx - 1]
            v1 = df[col][idx]
            if self.descending:
                return f"Values are not non-increasing ({v0} < {v1})"
            else:
                return f"Values are not non-decreasing ({v0} > {v1})"
        else:
            invalid_groups = df.filter(
                pl.col(col).sort(descending=self.descending).over(self.over) != pl.col(col)
            )[self.over].unique()
            n = len(invalid_groups)
            first_invalids = invalid_groups[:5].to_list()
            return f'Values are not sorted for {n:,} "{self.over}" groups ({first_invalids})'


class NonDecreasing(Sorted):
    """Guarantee for variables whose values are sorted in a non-decreasing order."""

    def __init__(self, **kwargs):
        super().__init__(descending=False, **kwargs)


class NonIncreasing(Sorted):
    """Guarantee for variables whose values are sorted in a non-increasing order."""

    def __init__(self, **kwargs):
        super().__init__(descending=True, **kwargs)


class LargerThan(Guarantee):
    """Guarantee for variables whose values are always larger than another variable (defined by a
    polars Expression).
    """

    def __init__(self, expr: pl.Expr, alias: str | None = None, strict: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.alias = alias or polars_expr_to_string(expr)
        self.expr = expr.alias(self.alias)
        self.strict = strict

    def is_valid_expr(self, col: str):
        if self.strict:
            return pl.col(col) > self.expr
        else:
            return pl.col(col) >= self.expr

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        return df.select(self.is_valid_expr(col)).to_series().all()

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        invalid_values = df.filter(self.is_valid_expr(col).not_()).select(col, self.expr)
        n = len(invalid_values)
        if self.strict:
            return f"{n} values are not larger than {self.alias}:\n{invalid_values}"
        else:
            return f"{n} values are smaller than {self.alias}:\n{invalid_values}"

    def _auto_fix(self, col: str) -> pl.Expr:
        return pl.when(self.is_valid_expr(col)).then(col).otherwise(pl.lit(self.fix_value))


class SmallerThan(Guarantee):
    """Guarantee for variables whose values are always smaller than another variable (defined by a
    polars Expression).
    """

    def __init__(self, expr: pl.Expr, alias: str | None = None, strict: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.alias = alias or polars_expr_to_string(expr)
        self.expr = expr.alias(self.alias)
        self.strict = strict

    def is_valid_expr(self, col: str):
        if self.strict:
            return pl.col(col) < self.expr
        else:
            return pl.col(col) <= self.expr

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        return df.select(self.is_valid_expr(col)).to_series().all()

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        invalid_values = df.filter(self.is_valid_expr(col).not_()).select(col, self.expr)
        n = len(invalid_values)
        if self.strict:
            return f"{n} values are not smaller than {self.alias}:\n{invalid_values}"
        else:
            return f"{n} values are larger than {self.alias}:\n{invalid_values}"

    def _auto_fix(self, col: str) -> pl.Expr:
        return pl.when(self.is_valid_expr(col)).then(col).otherwise(pl.lit(self.fix_value))


class LowerBounded(LargerThan):
    """Guarantee for variables that are lower bounded by a value."""

    def __init__(self, lower_bound, exclusive: bool = False, **kwargs):
        super().__init__(pl.lit(lower_bound), alias=str(lower_bound), strict=exclusive, **kwargs)

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        invalid_values = df.filter(self.is_valid_expr(col).not_())[col]
        n = len(invalid_values)
        first_invalids = invalid_values.unique()[:5].to_list()
        if self.strict:
            return f"{n:,} values are not larger than {self.alias} ({first_invalids})"
        else:
            return f"{n:,} values are smaller than {self.alias} ({first_invalids})"


class UpperBounded(SmallerThan):
    """Guarantee for variables that are upper bounded by a value."""

    def __init__(self, upper_bound, exclusive: bool = False, **kwargs):
        super().__init__(pl.lit(upper_bound), alias=str(upper_bound), strict=exclusive, **kwargs)

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        invalid_values = df.filter(self.is_valid_expr(col).not_())[col]
        n = len(invalid_values)
        first_invalids = invalid_values.unique()[:5].to_list()
        if self.strict:
            return f"{n:,} values are not smaller than {self.alias} ({first_invalids})"
        else:
            return f"{n:,} values are larger than {self.alias} ({first_invalids})"


class Bounded(MultipleGuarantees):
    """Guarantee for variables with a lower bound and upper bound."""

    def __init__(self, lower_bound, upper_bound, **kwargs):
        super().__init__(LowerBounded(lower_bound), UpperBounded(upper_bound), **kwargs)


class Positive(LowerBounded):
    """Guarantee for variables whose values are all positive."""

    def __init__(self, **kwargs):
        super().__init__(lower_bound=0, exclusive=True, **kwargs)


class NonNegative(LowerBounded):
    """Guarantee for variables whose values are all non-negative."""

    def __init__(self, **kwargs):
        super().__init__(lower_bound=0, exclusive=False, **kwargs)


class Indexed(Guarantee):
    """Guarantee for variables whose values range from 1 to the number of values."""

    def __init__(self, over: pl.Expr | None = None, over_alias: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.over = over
        self.over_alias = over_alias
        if over_alias is None and over is not None:
            self.over_alias = polars_expr_to_string(over)

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        if self.over is None:
            return df.select((pl.col(col) == pl.int_range(1, pl.len() + 1)).all()).item()
        else:
            return df.select(
                (pl.col(col) == pl.int_range(1, pl.len() + 1)).over(self.over).all()
            ).item()

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        msg = "Values do not range from 1 to the number of values"
        if self.over is None:
            m = df[col].min()
            if m < 1:
                return f"{msg} (found {m})"
            m = df[col].max()
            if m > len(df):
                return f"{msg} (found {m} > nb values)"
            diff = df[col].diff()
            idx = (diff != 1).arg_max()
            values = df[col][idx - 1 : idx + 1].to_list()
            return f"{msg} (values are not sorted: {values})"
        else:
            msg += f" over {self.over_alias}"
            return msg


class Defined(Guarantee):
    """Guarantee for variables whose values are non-null."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        return df[col].null_count() == 0

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        n = df[col].null_count()
        return f"{n:,} values are null"


class Null(Guarantee):
    """Guarantee for variables whose values are null."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        return df[col].null_count() == len(df)

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        n = len(df) - df[col].null_count()
        invalid_values = df[col].drop_nulls().unique()[:5].to_list()
        return f"{n:,} values are non-null ({invalid_values})"

    def _auto_fix(self, col: str) -> pl.Expr:
        return pl.lit(None)


class AllDefinedOrAllNull(Guarantee):
    """Guarantee for variables whose values are either all null or all non-null."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        null_count = df[col].null_count()
        return null_count == len(df) or null_count == 0

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        nulls = df[col].null_count()
        n = len(df)
        return f"Unexpected mix of null and defined values (nb nulls: {nulls}, nb values: {n:,})"


class DefinedIfAndOnlyIf(MultipleGuarantees):
    """Guarantee for variables whose values are all non-null when a condition is satisfied and all
    null when that same condition is not satisfied.
    """

    def __init__(self, cond: pl.Expr, alias: str | None = None, **kwargs):
        alias = alias or polars_expr_to_string(cond)
        super().__init__(
            Defined(when=cond, when_alias=alias),
            Null(when=cond.not_(), when_alias=f"NOT {alias}"),
            **kwargs,
        )


class ValidInsee(Guarantee):
    """Guarantee for variables whose values are valid INSEE codes."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def is_valid_expr(self, col: str):
        return (
            pl.col(col).str.contains(INSEE_REGEX)
            & pl.col(col).str.starts_with("96").not_()
            & pl.col(col).str.ends_with("000").not_()
            & pl.col(col).str.ends_with("999").not_()
        )

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        return df.select(self.is_valid_expr(col).all()).item()

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        invalid_values = df.filter(self.is_valid_expr(col).not_())[col][:5].to_list()
        return f"Found invalid INSEE codes:\n{invalid_values}"


class ValidDepCode(Guarantee):
    """Guarantee for variables whose values are valid departement codes."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        return df[col].is_in(NUTS_DF["dep_code"].to_list()).all()

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        invalid_values = df.filter(pl.col(col).is_in(NUTS_DF["dep_code"]))[col][:5].to_list()
        return f"Found invalid departement codes:\n{invalid_values}"


class InseeConsistentWithDep(Guarantee):
    def __init__(self, dep_col: str, **kwargs):
        super().__init__(**kwargs)
        self.dep_col = dep_col

    def is_valid_expr(self, col: str):
        return (
            pl.col(col).is_null()
            | pl.col(col).str.starts_with("99")
            | pl.col(self.dep_col).eq(pl.col(col).str.slice(0, 2))
            | pl.col(self.dep_col).eq(pl.col(col).str.slice(0, 3))
        )

    def _check(self, df: pl.DataFrame, col: str):
        return df.select(self.is_valid_expr(col).all()).item()

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        invalids = df.filter(self.is_valid_expr(col).not_()).select(col, self.dep_col)
        n = len(invalids)
        return f"{n:,} values are not consistent with `{self.dep_col}`:\n{invalids}"


class EqualTo(Guarantee):
    """Guarantee for variables whose values are always equal to another variable (defined by a
    polars Expression).
    """

    def __init__(self, expr: pl.Expr, alias: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.alias = alias or polars_expr_to_string(expr)
        self.expr = expr.alias(self.alias)

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        return df.select(pl.col(col) == self.expr).to_series().all()

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        invalid_values = df.filter(pl.col(col) != self.expr)[col]
        n = len(invalid_values)
        first_invalids = invalid_values.unique()[:5].to_list()
        return f"{n:,} values are different from {self.alias} ({first_invalids})"

    def _auto_fix(self, col: str) -> pl.Expr:
        return self.expr


class NotEqualTo(Guarantee):
    """Guarantee for variables whose values are always different from another variable (defined by a
    polars Expression).
    """

    def __init__(self, expr: pl.Expr, alias: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.alias = alias or polars_expr_to_string(expr)
        self.expr = expr.alias(self.alias)

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        return df.select(pl.col(col) != self.expr).to_series().all()

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        n = df.select((pl.col(col) == self.expr).sum()).item()
        return f"{n:,} values are equal to {self.alias}"

    def _auto_fix(self, col: str) -> pl.Expr:
        return (
            pl.when(pl.col(col).ne_missing(self.expr)).then(col).otherwise(pl.lit(self.fix_value))
        )


class ValueIs(EqualTo):
    """Guarantee for variables whose values are always equal to a given value."""

    def __init__(self, value, **kwargs):
        super().__init__(pl.lit(value), alias=f"{value}", **kwargs)


class ValueIsNot(NotEqualTo):
    """Guarantee for variables whose values are always different from a given value."""

    def __init__(self, value, **kwargs):
        super().__init__(pl.lit(value), alias=f"{value}", **kwargs)


class AtLeastOneOf(Guarantee):
    """Guarantee for variables where one specific value must appears at least once."""

    def __init__(self, value, over: pl.Expr | None = None, over_alias: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.over = over
        self.over_alias = over_alias
        if over_alias is None and over is not None:
            self.over_alias = polars_expr_to_string(over)

    def is_valid_expr(self, col: str):
        return pl.col(col).eq(self.value).any()

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        if self.over is None:
            return df.select(self.is_valid_expr(col)).item()
        else:
            return df.group_by(self.over).agg(valid=self.is_valid_expr(col))["valid"].all()

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        if self.over is None:
            return f"Value {self.value} never appears"
        else:
            invalid_groups = (
                df.group_by(self.over)
                .agg(valid=self.is_valid_expr(col))
                .filter(pl.col("valid").not_())
                .select(self.over)
                .to_series()
            )
            n = len(invalid_groups)
            first_invalids = invalid_groups[:5].to_list()
            return f"Value {self.value} never appears over {n:,} {self.over_alias} groups ({first_invalids})"

    def _auto_fix(self, col: str) -> pl.Expr:
        if self.over is None:
            return pl.when(self.is_valid_expr(col)).then(col).otherwise(pl.lit(self.fix_value))
        else:
            return (
                pl.when(self.is_valid_expr(col).over(self.over))
                .then(col)
                .otherwise(pl.lit(self.fix_value))
            )


class AtMostOneOf(Guarantee):
    """Guarantee for variables where one specific value must appears at most once."""

    def __init__(self, value, over: pl.Expr | None = None, over_alias: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.over = over
        self.over_alias = over_alias
        if over_alias is None and over is not None:
            self.over_alias = polars_expr_to_string(over)

    def is_valid_expr(self, col: str):
        return pl.col(col).eq(self.value).sum() <= 1

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        if self.over is None:
            return df.select(self.is_valid_expr(col)).item()
        else:
            return df.group_by(self.over).agg(valid=self.is_valid_expr(col))["valid"].all()

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        if self.over is None:
            n = df.select(self.is_valid_expr(col).not_().sum()).item()
            return f"Value {self.value} appears {n:,} times"
        else:
            invalid_groups = (
                df.group_by(self.over)
                .agg(valid=self.is_valid_expr(col))
                .filter(pl.col("valid").not_())
                .select(self.over)
                .to_series()
            )
            n = len(invalid_groups)
            first_invalids = invalid_groups[:5].to_list()
            return f"Value {self.value} appears more than once for {n:,} {self.over_alias} ({first_invalids})"

    def _auto_fix(self, col: str) -> pl.Expr:
        if self.over is None:
            return pl.when(self.is_valid_expr(col)).then(col).otherwise(pl.lit(self.fix_value))
        else:
            return (
                pl.when(self.is_valid_expr(col).over(self.over))
                .then(col)
                .otherwise(pl.lit(self.fix_value))
            )


class ExactlyOneOf(MultipleGuarantees):
    """Guarantee for variables where one specific value must appears exactly once."""

    def __init__(self, value, over: pl.Expr | None = None, over_alias: str | None = None, **kwargs):
        super().__init__(
            AtMostOneOf(value, over=over, over_alias=over_alias),
            AtLeastOneOf(value, over=over, over_alias=over_alias),
            **kwargs,
        )


class EqualToMapping(EqualTo):
    """Guarantee for variables whose values can be directly deducted by mapping other values."""

    def __init__(self, other: pl.Expr, alias: str, mapping: dict, **kwargs):
        super().__init__(
            other.replace_strict(mapping, default=None), f"mapping from {alias}", **kwargs
        )


class ValueInSet(Guarantee):
    """Guarantee for variables whose values are within a set."""

    def __init__(self, possible_values: set, **kwargs):
        super().__init__(**kwargs)
        self.possible_values = possible_values

    def is_valid_expr(self, col: str):
        return pl.col(col).is_in(self.possible_values)

    def _check(self, df: pl.DataFrame, col: str):
        return df.select(self.is_valid_expr(col).all()).item()

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        invalid_values = df.filter(self.is_valid_expr(col).not_())[col]
        n = len(invalid_values)
        first_invalids = invalid_values.unique()[:5].to_list()
        return f"{n:,} values are invalids ({first_invalids})"

    def _auto_fix(self, col: str) -> pl.Expr:
        return pl.when(self.is_valid_expr(col)).then(col).otherwise(pl.lit(self.fix_value))


class ListContains(Guarantee):
    """Guarantee for list variables that must contain a given expression in the list."""

    def __init__(self, expr: pl.Expr, alias: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.alias = alias or polars_expr_to_string(expr)
        self.expr = expr.alias(self.alias)

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        return df.select(pl.col(col).list.contains(self.expr)).to_series().all()

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        n = len(df.filter(pl.col(col).list.contains(self.expr).not_()))
        return f"{n:,} values do not contain {self.alias}"


class ListLengthIs(Guarantee):
    """Guarantee for list variables whose length must be equal to a given expression."""

    def __init__(self, expr: pl.Expr, alias: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.alias = alias or polars_expr_to_string(expr)
        self.expr = expr.alias(self.alias)

    def _check(self, df: pl.DataFrame, col: str) -> bool:
        return df.select(pl.col(col).list.len().eq(self.expr)).to_series().all()

    def _fail_msg(self, df: pl.DataFrame, col: str) -> str:
        invalid_values = df.filter(pl.col(col).list.len().ne(self.expr)).select(
            col, self.expr.alias(self.alias)
        )
        n = len(invalid_values)
        first_invalids = invalid_values[:5]
        return f"{n:,} values have not the expected length:\n{first_invalids}"
