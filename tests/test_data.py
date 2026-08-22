import pandas as pd
import pytest

from data import resolve_historical_tickers


def test_historical_proxy_resolution():
    weights = {"VTI": 0.45, "VXUS": 0.20, "AGG": 0.30, "SGOV": 0.05}
    resolved, substitutions = resolve_historical_tickers(
        weights, ["VTI", "VEU", "AGG", "SHY"]
    )
    assert resolved == {"VTI": 0.45, "VEU": 0.20, "AGG": 0.30, "SHY": 0.05}
    assert substitutions == {"VXUS": "VEU", "SGOV": "SHY"}


def test_proxy_resolution_never_silently_drops_asset():
    with pytest.raises(ValueError):
        resolve_historical_tickers({"MISSING": 1.0}, ["VTI", "AGG"])
