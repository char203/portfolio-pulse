from dataclasses import dataclass
from typing import List, Dict
import pandas as pd

RISK_BANDS = [(4, "Low"), (9, "Moderate"), (15, "High"), (25, "Critical")]

def risk_band(score: int) -> str:
    for ceiling, label in RISK_BANDS:
        if score <= ceiling:
            return label
    raise ValueError("Risk score must be between 1 and 25.")

def score_risk(likelihood: int, impact: int) -> Dict[str, object]:
    if not 1 <= likelihood <= 5 or not 1 <= impact <= 5:
        raise ValueError("Likelihood and impact must each be 1-5.")
    score = likelihood * impact
    return {"score": score, "band": risk_band(score)}

def assess_risk_register(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Inherent Score"] = out["Inherent Likelihood"] * out["Inherent Impact"]
    out["Inherent Rating"] = out["Inherent Score"].map(risk_band)
    out["Residual Score"] = out["Residual Likelihood"] * out["Residual Impact"]
    out["Residual Rating"] = out["Residual Score"].map(risk_band)
    return out

def evaluate_kri(name: str, value: float, green: float, amber: float, direction: str) -> str:
    if direction == "higher_is_better":
        return "GREEN" if value >= green else ("AMBER" if value >= amber else "RED")
    if direction == "lower_is_better":
        return "GREEN" if value <= green else ("AMBER" if value <= amber else "RED")
    raise ValueError("direction must be higher_is_better or lower_is_better")

def incident_trends(df: pd.DataFrame) -> Dict[str, object]:
    if df.empty:
        return {"total": 0, "recurring": 0, "by_category": {}, "by_severity": {}}
    return {
        "total": int(len(df)),
        "recurring": int(df["Recurring"].astype(str).str.upper().eq("Y").sum()),
        "by_category": df["Category"].value_counts().to_dict(),
        "by_severity": df["Severity"].value_counts().to_dict(),
    }
