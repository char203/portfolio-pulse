import pandas as pd

from attribution import (
    calculate_daily_contributions,
    reconcile_contributions,
)


def test_attribution_reconciles_to_portfolio_return():
    returns = pd.DataFrame(
        {
            "VTI": [0.01, -0.02, 0.015],
            "VXUS": [0.005, -0.01, 0.02],
            "AGG": [0.002, 0.003, -0.001],
            "SGOV": [0.0001, 0.0001, 0.0001],
        }
    )

    weights = {
        "VTI": 0.45,
        "VXUS": 0.20,
        "AGG": 0.30,
        "SGOV": 0.05,
    }

    contributions = calculate_daily_contributions(
        returns,
        weights,
    )

    portfolio_returns = (
        returns
        .mul(pd.Series(weights), axis="columns")
        .sum(axis=1)
    )

    assert reconcile_contributions(
        contributions,
        portfolio_returns,
    )
