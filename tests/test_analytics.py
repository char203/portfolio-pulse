import math
import pandas as pd

from analytics import (
    normalize_weights,
    portfolio_returns,
    annualized_volatility,
    max_drawdown,
)


def test_normalize_weights():
    w = normalize_weights({"A": 60, "B": 40})
    assert math.isclose(w.sum(), 1.0)
    assert math.isclose(w["A"], 0.6)


def test_portfolio_returns_weighted_average():
    r = pd.DataFrame({"A": [0.10, -0.10], "B": [0.00, 0.10]})
    p = portfolio_returns(r, {"A": 0.5, "B": 0.5})
    assert math.isclose(p.iloc[0], 0.05)
    assert math.isclose(p.iloc[1], 0.00, abs_tol=1e-12)


def test_zero_volatility():
    r = pd.Series([0.01] * 10)
    assert math.isclose(annualized_volatility(r), 0.0, abs_tol=1e-12)


def test_max_drawdown():
    r = pd.Series([0.10, -0.20, 0.05])
    assert math.isclose(max_drawdown(r), -0.20, rel_tol=1e-9)
