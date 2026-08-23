import pandas as pd
import pytest
from nfr import score_risk, evaluate_kri, incident_trends

def test_risk_scoring():
    result = score_risk(3, 4)
    assert result["score"] == 12
    assert result["band"] == "High"

def test_invalid_risk_score():
    with pytest.raises(ValueError):
        score_risk(0, 4)

def test_kri_thresholds():
    assert evaluate_kri("recon", 1.0, 1.0, .99, "higher_is_better") == "GREEN"
    assert evaluate_kri("failures", 2, 0, 1, "lower_is_better") == "RED"

def test_incident_trends():
    df = pd.DataFrame([
        {"Category": "Data", "Severity": "High", "Recurring": "Y"},
        {"Category": "Data", "Severity": "Medium", "Recurring": "N"},
        {"Category": "Technology", "Severity": "Medium", "Recurring": "Y"},
    ])
    trends = incident_trends(df)
    assert trends["total"] == 3
    assert trends["recurring"] == 2
    assert trends["by_category"]["Data"] == 2
