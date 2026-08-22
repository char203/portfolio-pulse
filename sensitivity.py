import pandas as pd


def build_sensitivity_scenarios(base_weights: dict[str, float]) -> dict[str, dict[str, float]]:
    """
    Create controlled allocation shifts around the base portfolio.

    The scenarios preserve a 100% total weight and are illustrative,
    not recommendations.
    """
    scenarios = {"Base": dict(base_weights)}

    def shifted(name, from_ticker, to_ticker, amount):
        w = dict(base_weights)
        if w[from_ticker] < amount:
            raise ValueError(
                f"Cannot shift {amount:.1%} from {from_ticker}; "
                f"base weight is only {w[from_ticker]:.1%}."
            )
        w[from_ticker] -= amount
        w[to_ticker] += amount
        scenarios[name] = w

    shifted("5% Equity -> Bonds", "VTI", "AGG", 0.05)
    shifted("10% Equity -> Bonds", "VTI", "AGG", 0.10)
    shifted("5% Bonds -> Equity", "AGG", "VTI", 0.05)
    shifted("10% Bonds -> Equity", "AGG", "VTI", 0.10)

    return scenarios


def validate_scenarios(scenarios: dict[str, dict[str, float]]) -> None:
    for name, weights in scenarios.items():
        total = sum(weights.values())
        if abs(total - 1.0) > 1e-10:
            raise ValueError(f"{name} does not sum to 100%: {total:.8f}")
        for ticker, weight in weights.items():
            if weight < 0 or weight > 1:
                raise ValueError(
                    f"{name}: invalid weight for {ticker}: {weight:.2%}"
                )


def sensitivity_table(results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for name, result in results.items():
        stats = result["portfolio_stats"]
        rows.append(
            {
                "Scenario": name,
                "CAGR": stats["annualized_return"],
                "Volatility": stats["annualized_volatility"],
                "Sharpe": stats["sharpe_ratio"],
                "Max Drawdown": stats["max_drawdown"],
                "Ending Value": float(result["portfolio_wealth"].iloc[-1]),
            }
        )
    return pd.DataFrame(rows)
