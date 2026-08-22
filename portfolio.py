"""Transparent, illustrative portfolio construction rules."""
from __future__ import annotations

from dataclasses import dataclass

ETF_LABELS = {
    "VTI": "US Equity",
    "VXUS": "International Equity",
    "AGG": "US Investment-Grade Bonds",
    "SGOV": "Short-Term US Treasuries",
}

@dataclass(frozen=True)
class InvestorProfile:
    objective: str
    horizon_years: int
    risk_tolerance: int  # 1-10
    portfolio_value: float = 10_000.0


def illustrative_allocation(profile: InvestorProfile) -> dict[str, float]:
    """Return a transparent educational allocation, not personalized advice.

    The rules intentionally use broad bands rather than an optimizer so every output
    can be explained and audited during the MVP stage.
    """
    r = max(1, min(10, int(profile.risk_tolerance)))

    # Base equity allocation from risk tolerance.
    equity = 0.30 + (r - 1) * (0.60 / 9)  # 30% to 90%

    # Short horizons constrain equity risk capacity.
    if profile.horizon_years < 3:
        equity = min(equity, 0.40)
    elif profile.horizon_years < 7:
        equity = min(equity, 0.65)

    objective = profile.objective.lower()
    if "preservation" in objective:
        equity = min(equity, 0.40)
    elif "income" in objective:
        equity = min(equity, 0.55)
    elif "long-term" in objective or "growth" in objective:
        equity = min(max(equity, 0.50), 0.90)

    cash = 0.05 if profile.horizon_years >= 7 else 0.10
    bonds = max(0.0, 1.0 - equity - cash)
    us_equity = equity * 0.70
    intl_equity = equity * 0.30

    return {
        "VTI": round(us_equity, 4),
        "VXUS": round(intl_equity, 4),
        "AGG": round(bonds, 4),
        "SGOV": round(cash, 4),
    }


def benchmark_60_40() -> dict[str, float]:
    return {"VTI": 0.60, "AGG": 0.40}
