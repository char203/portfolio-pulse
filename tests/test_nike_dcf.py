import pandas as pd
import pytest
from nike_dcf import build_nike_forecast,wacc,dcf,sensitivity

def sample():
    h=pd.DataFrame([{"Revenue":46398,"Operating NWC":9832,"Diluted Shares":1481,"Debt":7942,"Cash":7563,"Short-Term Investments":1464}])
    a=pd.DataFrame([
        {"Year":2027,"Revenue Growth":.02,"EBIT Margin":.09,"Tax Rate":.21,"D&A % Revenue":.016,"Capex % Revenue":.016,"NWC % Revenue":.212},
        {"Year":2028,"Revenue Growth":.04,"EBIT Margin":.105,"Tax Rate":.21,"D&A % Revenue":.016,"Capex % Revenue":.016,"NWC % Revenue":.210},
    ])
    return h,a

def test_year_one_delta_nwc_uses_actual_base():
    h,a=sample()
    f=build_nike_forecast(h,a)
    assert f.iloc[0]["Change in NWC"] != 0

def test_revenue_forecast_compounds():
    h,a=sample()
    f=build_nike_forecast(h,a)
    assert f.iloc[0]["Revenue"] == pytest.approx(46398*1.02)
    assert f.iloc[1]["Revenue"] == pytest.approx(46398*1.02*1.04)

def test_wacc_between_debt_and_equity_costs():
    result=wacc(.04,1,.05,.045,.21,60000,8000)
    assert .035 < result < .09

def test_dcf_bridge_with_net_cash():
    h,a=sample(); f=build_nike_forecast(h,a)
    r=dcf(f,.08,.025,-1000,1000)
    assert r["equity_value"] > r["enterprise_value"]

def test_sensitivity_direction():
    h,a=sample(); f=build_nike_forecast(h,a)
    s=sensitivity(f,0,1000,[.07,.09],[.02,.03])
    assert s.loc[.07,.02] > s.loc[.09,.02]
    assert s.loc[.08 if .08 in s.index else .07,.03] > s.loc[.07,.02]
