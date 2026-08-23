from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ControlResult:
    control: str
    rule: str
    actual: float | str
    status: str
    severity: str
    remediation: str


DEFAULT_POLICY = {
    "max_single_asset_weight": 0.50,
    "max_equity_weight": 0.80,
    "min_international_weight": 0.10,
    "min_liquidity_weight": 0.05,
    "max_volatility": 0.20,
    "max_drawdown": 0.25,
    "weight_tolerance": 0.0001,
}


def evaluate_portfolio_controls(
    weights: Dict[str, float],
    annualized_volatility: float,
    max_drawdown: float,
    policy: Dict[str, float] | None = None,
) -> List[ControlResult]:
    p = dict(DEFAULT_POLICY)
    if policy:
        p.update(policy)

    results: List[ControlResult] = []

    total_weight = sum(weights.values())
    total_ok = abs(total_weight - 1.0) <= p["weight_tolerance"]
    results.append(ControlResult(
        "Portfolio Weight Total",
        "Weights must sum to 100%",
        total_weight,
        "PASS" if total_ok else "FAIL",
        "High",
        "-" if total_ok else "Rebalance weights to total 100%.",
    ))

    max_ticker = max(weights, key=weights.get)
    max_weight = weights[max_ticker]
    single_ok = max_weight <= p["max_single_asset_weight"]
    results.append(ControlResult(
        "Single-Asset Concentration",
        f"No holding > {p['max_single_asset_weight']:.0%}",
        max_weight,
        "PASS" if single_ok else "FAIL",
        "Medium",
        "-" if single_ok else f"Reduce {max_ticker} concentration.",
    ))

    equity_weight = weights.get("VTI", 0.0) + weights.get("VXUS", 0.0)
    equity_ok = equity_weight <= p["max_equity_weight"]
    results.append(ControlResult(
        "Equity Allocation",
        f"Equity allocation <= {p['max_equity_weight']:.0%}",
        equity_weight,
        "PASS" if equity_ok else "FAIL",
        "High",
        "-" if equity_ok else "Reduce equity exposure.",
    ))

    international_weight = weights.get("VXUS", 0.0)
    international_ok = international_weight >= p["min_international_weight"]
    results.append(ControlResult(
        "International Diversification",
        f"International allocation >= {p['min_international_weight']:.0%}",
        international_weight,
        "PASS" if international_ok else "FAIL",
        "Low",
        "-" if international_ok else "Increase international allocation.",
    ))

    liquidity_weight = weights.get("SGOV", 0.0)
    liquidity_ok = liquidity_weight >= p["min_liquidity_weight"]
    results.append(ControlResult(
        "Liquidity Floor",
        f"Short-term Treasury allocation >= {p['min_liquidity_weight']:.0%}",
        liquidity_weight,
        "PASS" if liquidity_ok else "FAIL",
        "Medium",
        "-" if liquidity_ok else "Increase short-term Treasury allocation.",
    ))

    vol_ok = annualized_volatility <= p["max_volatility"]
    results.append(ControlResult(
        "Portfolio Volatility Limit",
        f"Annualized volatility <= {p['max_volatility']:.0%}",
        annualized_volatility,
        "PASS" if vol_ok else "FAIL",
        "Medium",
        "-" if vol_ok else "Review risk allocation and reduce volatile exposures.",
    ))

    drawdown_ok = abs(max_drawdown) <= p["max_drawdown"]
    results.append(ControlResult(
        "Maximum Drawdown Limit",
        f"Historical max drawdown <= {p['max_drawdown']:.0%}",
        abs(max_drawdown),
        "PASS" if drawdown_ok else "FAIL",
        "High",
        "-" if drawdown_ok else "Review allocation and downside-risk exposure.",
    ))

    return results


def controls_summary(results: List[ControlResult]) -> dict:
    total = len(results)
    passed = sum(r.status == "PASS" for r in results)
    failed = total - passed
    return {
        "total_controls": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / total if total else 0.0,
        "overall_status": "PASS" if failed == 0 else "EXCEPTIONS",
    }
