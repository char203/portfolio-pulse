"""Core portfolio analytics for Portfolio Pulse."""
from __future__ import annotations

import math
from typing import Mapping
import numpy as np
import pandas as pd

TRADING_DAYS = 252


def normalize_weights(weights: Mapping[str, float]) -> pd.Series:
    s = pd.Series(weights, dtype=float)
    if (s < 0).any():
        raise ValueError("Long-only MVP: portfolio weights cannot be negative.")
    total = s.sum()
    if total <= 0:
        raise ValueError("Portfolio weights must sum to a positive value.")
    return s / total


def portfolio_returns(asset_returns: pd.DataFrame, weights: Mapping[str, float]) -> pd.Series:
    w = normalize_weights(weights)
    missing = [ticker for ticker in w.index if ticker not in asset_returns.columns]
    if missing:
        raise KeyError(f"Missing return series for: {', '.join(missing)}")
    aligned = asset_returns[w.index]
    return aligned.mul(w, axis=1).sum(axis=1).rename("portfolio_return")


def annualized_return(returns: pd.Series, periods_per_year: int = TRADING_DAYS) -> float:
    if returns.empty:
        return float("nan")
    growth = float((1 + returns).prod())
    years = len(returns) / periods_per_year
    if growth <= 0 or years <= 0:
        return float("nan")
    return growth ** (1 / years) - 1


def annualized_volatility(returns: pd.Series, periods_per_year: int = TRADING_DAYS) -> float:
    return float(returns.std(ddof=1) * math.sqrt(periods_per_year))


def sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS,
) -> float:
    vol = annualized_volatility(returns, periods_per_year)
    if vol == 0 or np.isnan(vol):
        return float("nan")
    return (annualized_return(returns, periods_per_year) - risk_free_rate) / vol


def wealth_index(returns: pd.Series, initial_value: float = 10_000.0) -> pd.Series:
    return initial_value * (1 + returns).cumprod()


def drawdown_series(returns: pd.Series) -> pd.Series:
    wealth = (1 + returns).cumprod()
    peak = wealth.cummax()
    return wealth / peak - 1


def max_drawdown(returns: pd.Series) -> float:
    dd = drawdown_series(returns)
    return float(dd.min())


def max_drawdown_details(returns: pd.Series) -> dict:
    wealth = (1 + returns).cumprod()
    peak = wealth.cummax()
    dd = wealth / peak - 1
    trough = dd.idxmin()
    peak_date = wealth.loc[:trough].idxmax()
    previous_peak = wealth.loc[peak_date]
    recovered = wealth.loc[trough:] >= previous_peak
    recovery_date = recovered[recovered].index.min() if recovered.any() else pd.NaT
    return {
        "max_drawdown": float(dd.loc[trough]),
        "peak_date": peak_date,
        "trough_date": trough,
        "recovery_date": recovery_date,
    }


def correlation_matrix(asset_returns: pd.DataFrame) -> pd.DataFrame:
    return asset_returns.corr()


def beta(returns: pd.Series, benchmark_returns: pd.Series) -> float:
    aligned = pd.concat([returns, benchmark_returns], axis=1).dropna()
    if aligned.shape[0] < 2:
        return float("nan")
    benchmark_var = float(aligned.iloc[:, 1].var(ddof=1))
    if benchmark_var == 0:
        return float("nan")
    covariance = float(aligned.iloc[:, 0].cov(aligned.iloc[:, 1]))
    return covariance / benchmark_var


def summary_statistics(
    returns: pd.Series,
    benchmark_returns: pd.Series | None = None,
    risk_free_rate: float = 0.0,
) -> dict:
    stats = {
        "annualized_return": annualized_return(returns),
        "annualized_volatility": annualized_volatility(returns),
        "sharpe_ratio": sharpe_ratio(returns, risk_free_rate=risk_free_rate),
        "max_drawdown": max_drawdown(returns),
    }
    if benchmark_returns is not None:
        stats["beta"] = beta(returns, benchmark_returns)
        stats["excess_annualized_return"] = annualized_return(returns) - annualized_return(benchmark_returns)
    return stats
