"""Market data utilities for Portfolio Pulse.

Design principle: current portfolio analytics use the actual selected ETFs. Historical
stress tests may use explicitly disclosed proxy ETFs when the current ETF did not yet
exist. We never silently backfill a fund before inception.
"""
from __future__ import annotations

from typing import Iterable, Mapping
import pandas as pd

CURRENT_TICKERS = ["VTI", "VXUS", "AGG", "SGOV"]

# Historical proxies used only when a selected ETF did not yet exist.
# VEU: broad ex-US equity ETF, available from 2007.
# SHY: 1-3Y Treasury ETF, available from 2002; imperfect but transparent proxy
# for the cash/short-Treasury sleeve before SGOV's 2020 inception.
HISTORICAL_PROXY_MAP = {
    "VXUS": "VEU",
    "SGOV": "SHY",
}


def download_adjusted_close(
    tickers: Iterable[str],
    start: str,
    end: str | None = None,
    *,
    drop_incomplete: bool = True,
) -> pd.DataFrame:
    """Download adjusted price history from Yahoo Finance.

    yfinance ``auto_adjust=True`` incorporates splits and distributions into the
    adjusted series. ``drop_incomplete=False`` is useful for diagnosing fund
    inception gaps instead of silently deleting early history.
    """
    tickers = list(dict.fromkeys(tickers))
    if not tickers:
        raise ValueError("At least one ticker is required.")

    try:
        import yfinance as yf
    except ImportError as exc:
        raise ImportError("Install project dependencies with: pip install -r requirements.txt") from exc

    raw = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        group_by="column",
        threads=True,
    )
    if raw.empty:
        raise ValueError("No market data returned. Check tickers/date range/network.")

    if len(tickers) == 1:
        close = raw[["Close"]].rename(columns={"Close": tickers[0]})
    else:
        close = raw["Close"].copy()
        close = close.reindex(columns=tickers)

    close = close.sort_index()
    if drop_incomplete:
        close = close.dropna(how="any")
    else:
        close = close.dropna(how="all")
    if close.empty:
        raise ValueError("No usable price history across the selected tickers.")
    return close


def to_returns(prices: pd.DataFrame, *, drop_incomplete: bool = True) -> pd.DataFrame:
    """Convert adjusted price levels to simple periodic returns."""
    returns = prices.pct_change(fill_method=None)
    returns = returns.dropna(how="any" if drop_incomplete else "all")
    if returns.empty:
        raise ValueError("Insufficient price history to calculate returns.")
    return returns


def first_valid_dates(prices: pd.DataFrame) -> pd.Series:
    """Return the first observed price date for every ticker."""
    return prices.apply(lambda s: s.first_valid_index())


def resolve_historical_tickers(
    desired_weights: Mapping[str, float],
    available_columns: Iterable[str],
    proxy_map: Mapping[str, str] = HISTORICAL_PROXY_MAP,
) -> tuple[dict[str, float], dict[str, str]]:
    """Resolve desired holdings to actual or proxy series available in a period.

    Returns ``(resolved_weights, substitutions)``. Raises rather than dropping an
    asset silently, because changing portfolio composition would invalidate the test.
    """
    available = set(available_columns)
    resolved: dict[str, float] = {}
    substitutions: dict[str, str] = {}

    for ticker, weight in desired_weights.items():
        if ticker in available:
            resolved[ticker] = resolved.get(ticker, 0.0) + float(weight)
            continue
        proxy = proxy_map.get(ticker)
        if proxy and proxy in available:
            resolved[proxy] = resolved.get(proxy, 0.0) + float(weight)
            substitutions[ticker] = proxy
            continue
        raise ValueError(
            f"No historical series available for {ticker}; add a documented proxy "
            "or choose a later analysis period."
        )
    return resolved, substitutions
