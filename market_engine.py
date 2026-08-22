"""Step 2 orchestration: current portfolio + benchmark + historical stress tests."""
from __future__ import annotations

from typing import Mapping
import pandas as pd

from analytics import portfolio_returns, summary_statistics, wealth_index
from data import download_adjusted_close, to_returns
from scenarios import SCENARIOS, evaluate_scenario

DEFAULT_WEIGHTS = {"VTI": 0.45, "VXUS": 0.20, "AGG": 0.30, "SGOV": 0.05}
BENCHMARK_WEIGHTS = {"VTI": 0.60, "AGG": 0.40}


def run_current_analysis(
    weights: Mapping[str, float] = DEFAULT_WEIGHTS,
    start: str = "2020-06-01",
    end: str | None = None,
    initial_value: float = 10_000.0,
) -> dict:
    """Run current-ETF analysis from a common live-history start date."""
    tickers = sorted(set(weights) | set(BENCHMARK_WEIGHTS))
    prices = download_adjusted_close(tickers, start, end, drop_incomplete=True)
    returns = to_returns(prices)
    portfolio = portfolio_returns(returns, weights)
    benchmark = portfolio_returns(returns, BENCHMARK_WEIGHTS).rename("benchmark_return")
    return {
        "prices": prices,
        "asset_returns": returns,
        "portfolio_returns": portfolio,
        "benchmark_returns": benchmark,
        "portfolio_wealth": wealth_index(portfolio, initial_value),
        "benchmark_wealth": wealth_index(benchmark, initial_value),
        "portfolio_stats": summary_statistics(portfolio, benchmark),
        "benchmark_stats": summary_statistics(benchmark),
    }


def run_stress_tests(
    weights: Mapping[str, float] = DEFAULT_WEIGHTS,
) -> pd.DataFrame:
    """Run all named scenarios using actual ETFs where possible and disclosed proxies otherwise."""
    # Include both current holdings and historical proxies in one diagnostic download.
    tickers = ["VTI", "VXUS", "VEU", "AGG", "SGOV", "SHY"]
    prices = download_adjusted_close(tickers, "2008-08-01", None, drop_incomplete=False)
    rows = [evaluate_scenario(prices, weights, scenario) for scenario in SCENARIOS.values()]
    return pd.DataFrame(rows)

if __name__ == "__main__":
    print("\nPORTFOLIO PULSE — CURRENT ANALYSIS")
    print("=" * 50)

    results = run_current_analysis()

    print("\nPortfolio statistics:")
    for metric, value in results["portfolio_stats"].items():
        print(f"{metric}: {value}")

    print("\n60/40 Benchmark statistics:")
    for metric, value in results["benchmark_stats"].items():
        print(f"{metric}: {value}")

    print("\nEnding values:")
    print(f"Portfolio: ${results['portfolio_wealth'].iloc[-1]:,.2f}")
    print(f"60/40 Benchmark: ${results['benchmark_wealth'].iloc[-1]:,.2f}")

    print("\nHISTORICAL STRESS TESTS")
    print("=" * 50)
    print(run_stress_tests().to_string(index=False))
