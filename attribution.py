import pandas as pd


def calculate_daily_contributions(
    asset_returns: pd.DataFrame,
    weights: dict[str, float],
) -> pd.DataFrame:
    """
    Calculate each asset's arithmetic contribution to daily portfolio return.

    contribution(i,t) = weight(i) * return(i,t)
    """

    missing = set(weights) - set(asset_returns.columns)

    if missing:
        raise ValueError(
            f"Missing return series for: {sorted(missing)}"
        )

    weight_series = pd.Series(weights)

    contributions = (
        asset_returns[list(weights.keys())]
        .mul(weight_series, axis="columns")
    )

    return contributions


def reconcile_contributions(
    contributions: pd.DataFrame,
    portfolio_returns: pd.Series,
    tolerance: float = 1e-10,
) -> bool:
    """
    Verify that asset contributions sum to the portfolio return for each period.
    """

    attributed_return = contributions.sum(axis=1)

    aligned = pd.concat(
        [
            attributed_return.rename("attributed"),
            portfolio_returns.rename("portfolio"),
        ],
        axis=1,
        join="inner",
    ).dropna()

    difference = (
        aligned["attributed"] -
        aligned["portfolio"]
    ).abs()

    return bool((difference <= tolerance).all())


def summarize_contributions(
    contributions: pd.DataFrame,
) -> pd.Series:
    """
    Sum daily arithmetic contributions across the analysis period.

    IMPORTANT:
    This is cumulative arithmetic contribution, not compounded return attribution.
    """

    return contributions.sum().sort_values(ascending=False)
