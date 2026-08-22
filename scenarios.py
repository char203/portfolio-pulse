"""Historical stress-test definitions and evaluation helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
import pandas as pd

from analytics import max_drawdown_details, portfolio_returns
from data import resolve_historical_tickers, to_returns


@dataclass(frozen=True)
class Scenario:
    name: str
    start: str
    end: str
    description: str


SCENARIOS = {
    "gfc": Scenario(
        "Global Financial Crisis",
        "2008-09-01",
        "2009-06-30",
        "Equity/credit crisis window. Uses disclosed proxies where current ETFs did not yet exist.",
    ),
    "covid": Scenario(
        "COVID Shock",
        "2020-02-19",
        "2020-08-31",
        "Rapid equity selloff followed by an unusually fast recovery.",
    ),
    "rates_2022": Scenario(
        "2022 Inflation / Rate Shock",
        "2022-01-03",
        "2022-12-30",
        "Inflation and rising yields pressured both equities and duration-sensitive bonds.",
    ),
}


def evaluate_scenario(
    prices: pd.DataFrame,
    desired_weights: Mapping[str, float],
    scenario: Scenario,
) -> dict:
    """Evaluate a portfolio in one historical scenario using transparent proxies."""
    window = prices.loc[scenario.start:scenario.end].copy()
    if window.empty:
        raise ValueError(f"No observations for scenario: {scenario.name}")

    # A ticker is considered available only if it has observations across the scenario.
    available = [c for c in window.columns if window[c].notna().all()]
    resolved_weights, substitutions = resolve_historical_tickers(desired_weights, available)
    used_prices = window[list(resolved_weights)].dropna(how="any")
    returns = to_returns(used_prices)
    port = portfolio_returns(returns, resolved_weights)

    details = max_drawdown_details(port)
    period_return = float((1 + port).prod() - 1)
    return {
        "scenario": scenario.name,
        "start": used_prices.index.min(),
        "end": used_prices.index.max(),
        "period_return": period_return,
        **details,
        "substitutions": substitutions,
        "series_used": list(resolved_weights),
        "description": scenario.description,
    }
