import streamlit as st
import pandas as pd
from pathlib import Path

from market_engine import run_current_analysis, run_stress_tests
from attribution import calculate_daily_contributions, summarize_contributions
from sensitivity import build_sensitivity_scenarios, sensitivity_table
from controls import evaluate_portfolio_controls, controls_summary
from nfr import assess_risk_register, evaluate_kri, incident_trends
from nike_dcf import (
    build_nike_forecast,
    wacc as calc_dcf_wacc,
    dcf as run_company_dcf,
    sensitivity as dcf_sensitivity,
)

st.set_page_config(
    page_title="Portfolio Pulse",
    page_icon="📈",
    layout="wide",
)

st.title("Portfolio Pulse")
st.caption(
    "Interactive multi-asset portfolio analytics, investment controls, "
    "non-financial risk monitoring, and company valuation"
)

# ============================================================
# SIDEBAR — PORTFOLIO INPUTS
# ============================================================

with st.sidebar:
    st.header("Portfolio Inputs")

    portfolio_value = st.number_input(
        "Hypothetical portfolio value ($)",
        min_value=1000,
        value=10000,
        step=1000,
    )

    st.subheader("Allocation")

    vti = st.slider("VTI — US Equity", 0, 100, 45)
    vxus = st.slider("VXUS — International Equity", 0, 100, 20)
    agg = st.slider("AGG — US Bonds", 0, 100, 30)
    sgov = st.slider("SGOV — Short-Term Treasuries", 0, 100, 5)

    total = vti + vxus + agg + sgov
    st.metric("Total allocation", f"{total}%")

    if total != 100:
        st.error("Weights must sum to 100%.")
        st.stop()

weights = {
    "VTI": vti / 100,
    "VXUS": vxus / 100,
    "AGG": agg / 100,
    "SGOV": sgov / 100,
}

with st.spinner("Running portfolio analytics..."):
    current = run_current_analysis(
        weights=weights,
        initial_value=float(portfolio_value),
    )
    stress = run_stress_tests(weights=weights)

p = current["portfolio_stats"]
b = current["benchmark_stats"]

# ============================================================
# PORTFOLIO SNAPSHOT
# ============================================================

st.subheader("Portfolio Snapshot")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Annualized Return",
    f"{p['annualized_return']:.2%}",
    f"{(p['annualized_return'] - b['annualized_return']):.2%} vs 60/40",
)
c2.metric("Annualized Volatility", f"{p['annualized_volatility']:.2%}")
c3.metric("Sharpe Ratio", f"{p['sharpe_ratio']:.2f}")
c4.metric("Max Drawdown", f"{p['max_drawdown']:.2%}")

c5, c6, c7 = st.columns(3)

c5.metric("Beta vs 60/40", f"{p['beta']:.2f}")
c6.metric(
    "Ending Portfolio Value",
    f"${current['portfolio_wealth'].iloc[-1]:,.0f}",
)
c7.metric(
    "Ending 60/40 Value",
    f"${current['benchmark_wealth'].iloc[-1]:,.0f}",
)

# ============================================================
# PORTFOLIO CONTROLS
# ============================================================

st.divider()
st.subheader("Portfolio Controls & Exceptions")

control_results = evaluate_portfolio_controls(
    weights=weights,
    annualized_volatility=p["annualized_volatility"],
    max_drawdown=p["max_drawdown"],
)

control_summary = controls_summary(control_results)

cc1, cc2, cc3 = st.columns(3)

cc1.metric(
    "Controls Passed",
    f"{control_summary['passed']}/{control_summary['total_controls']}",
)
cc2.metric("Exceptions", control_summary["failed"])
cc3.metric("Overall Status", control_summary["overall_status"])

controls_df = pd.DataFrame(
    [
        {
            "Control": r.control,
            "Rule": r.rule,
            "Actual": r.actual,
            "Status": r.status,
            "Severity": r.severity,
            "Remediation": r.remediation,
        }
        for r in control_results
    ]
)


def format_control_actual(value):
    if isinstance(value, (int, float)):
        return f"{value:.2%}"
    return value


controls_df["Actual"] = controls_df["Actual"].map(format_control_actual)

st.dataframe(
    controls_df,
    width="stretch",
    hide_index=True,
)

st.caption(
    "Illustrative investment-policy controls for educational analysis. "
    "These are project-defined rules, not regulatory requirements."
)

# ============================================================
# NON-FINANCIAL RISK / RCSA-STYLE MONITORING
# ============================================================

st.divider()
st.subheader("Non-Financial Risk & Control Monitoring")

risk_register_path = Path("nfr_data") / "risk_register.csv"
incidents_path = Path("nfr_data") / "incidents.csv"

risk_register = pd.read_csv(risk_register_path)
risk_register = assess_risk_register(risk_register)

nr1, nr2, nr3 = st.columns(3)

nr1.metric("Risks Assessed", len(risk_register))
nr2.metric(
    "High/Critical Inherent",
    int(
        risk_register["Inherent Rating"]
        .isin(["High", "Critical"])
        .sum()
    ),
)
nr3.metric(
    "High/Critical Residual",
    int(
        risk_register["Residual Rating"]
        .isin(["High", "Critical"])
        .sum()
    ),
)

st.markdown("#### RCSA-Style Risk Register")

risk_display = risk_register[
    [
        "Risk ID",
        "Category",
        "Risk",
        "Inherent Score",
        "Inherent Rating",
        "Control",
        "Control Type",
        "Automation",
        "Residual Score",
        "Residual Rating",
    ]
].copy()

st.dataframe(
    risk_display,
    width="stretch",
    hide_index=True,
)

st.markdown("#### Key Risk Indicators")

kri_rows = [
    {
        "KRI": "Attribution reconciliation rate",
        "Value": "100.00%",
        "Status": evaluate_kri(
            "Attribution reconciliation rate",
            1.00,
            1.00,
            0.99,
            "higher_is_better",
        ),
    },
    {
        "KRI": "Failed automated tests",
        "Value": "0",
        "Status": evaluate_kri(
            "Failed automated tests",
            0,
            0,
            1,
            "lower_is_better",
        ),
    },
    {
        "KRI": "Portfolio-control exceptions",
        "Value": str(control_summary["failed"]),
        "Status": evaluate_kri(
            "Portfolio-control exceptions",
            control_summary["failed"],
            0,
            1,
            "lower_is_better",
        ),
    },
]

st.dataframe(
    pd.DataFrame(kri_rows),
    width="stretch",
    hide_index=True,
)

st.markdown("#### Incident & Issue Trends")

incidents = pd.read_csv(incidents_path)
trends = incident_trends(incidents)

it1, it2 = st.columns(2)

it1.metric("Logged Issues", trends["total"])
it2.metric("Recurring Issues", trends["recurring"])

category_counts = incidents["Category"].value_counts().rename("Incidents")
st.bar_chart(category_counts)

with st.expander("Incident log"):
    st.dataframe(
        incidents,
        width="stretch",
        hide_index=True,
    )

st.caption(
    "Educational NFR-style framework using RCSA-style scoring and "
    "project-defined KRIs. It is not a bank's proprietary risk methodology "
    "or a regulatory compliance system."
)

# ============================================================
# WEALTH CURVE
# ============================================================

st.divider()
st.subheader("Growth of Portfolio")

wealth_df = pd.DataFrame(
    {
        "Portfolio Pulse": current["portfolio_wealth"],
        "60/40 Benchmark": current["benchmark_wealth"],
    }
)

st.line_chart(wealth_df)

ending_diff = (
    current["portfolio_wealth"].iloc[-1]
    - current["benchmark_wealth"].iloc[-1]
)

st.caption(
    f"Historical ending-value difference vs. 60/40: ${ending_diff:,.0f}"
)

# ============================================================
# HISTORICAL STRESS TESTS
# ============================================================

st.divider()
st.subheader("Historical Stress Tests")

stress_display = stress[
    [
        "scenario",
        "period_return",
        "max_drawdown",
        "recovery_date",
    ]
].copy()

stress_display["period_return"] = stress_display["period_return"].map(
    lambda x: f"{x:.2%}"
)

stress_display["max_drawdown"] = stress_display["max_drawdown"].map(
    lambda x: f"{x:.2%}"
)

stress_display["recovery_date"] = stress_display["recovery_date"].apply(
    lambda x: (
        "Not recovered by scenario end"
        if pd.isna(x)
        else pd.Timestamp(x).strftime("%Y-%m-%d")
    )
)

stress_display.columns = [
    "Scenario",
    "Period Return",
    "Max Drawdown",
    "Recovery",
]

st.dataframe(
    stress_display,
    width="stretch",
    hide_index=True,
)

st.caption(
    "Historical scenarios describe how the selected allocation behaved "
    "in prior market environments. They are not forecasts."
)

# ============================================================
# RETURN ATTRIBUTION
# ============================================================

st.divider()
st.subheader("Return Drivers")

asset_returns = current["asset_returns"][list(weights.keys())]

contributions = calculate_daily_contributions(
    asset_returns,
    weights,
)

summary = summarize_contributions(contributions)

attr_df = pd.DataFrame(
    {
        "Asset": summary.index,
        "Cumulative Arithmetic Contribution": summary.values,
    }
).set_index("Asset")

st.bar_chart(attr_df)

st.caption(
    "Attribution is the sum of daily arithmetic contributions "
    "(portfolio weight × asset return). It is not Brinson attribution."
)

# ============================================================
# ALLOCATION SENSITIVITY
# ============================================================

st.divider()
st.subheader("Allocation Sensitivity")

scenarios = build_sensitivity_scenarios(weights)

scenario_results = {
    name: run_current_analysis(
        weights=scenario_weights,
        initial_value=float(portfolio_value),
    )
    for name, scenario_weights in scenarios.items()
}

sens = sensitivity_table(scenario_results)
sens_display = sens.copy()

for col in ["CAGR", "Volatility", "Max Drawdown"]:
    sens_display[col] = sens_display[col].map(lambda x: f"{x:.2%}")

sens_display["Sharpe"] = sens_display["Sharpe"].map(
    lambda x: f"{x:.2f}"
)

sens_display["Ending Value"] = sens_display["Ending Value"].map(
    lambda x: f"${x:,.0f}"
)

st.dataframe(
    sens_display,
    width="stretch",
    hide_index=True,
)

chart_df = sens.set_index("Scenario")[["CAGR", "Max Drawdown"]]
st.bar_chart(chart_df)

st.caption(
    "Sensitivity scenarios apply controlled ±5% and ±10% shifts between "
    "VTI and AGG while holding other sleeves constant."
)

# ============================================================
# COMPANY VALUATION — NIKE DCF
# ============================================================

st.divider()
st.header("Company Valuation")
st.caption(
    "Illustrative DCF case study using NIKE, Inc. FY2024–FY2026 "
    "reported financials and project-defined forecast assumptions."
)

nike_hist = pd.read_csv(
    Path("valuation_data") / "nike_historicals.csv"
)
nike_ass = pd.read_csv(
    Path("valuation_data") / "nike_forecast_assumptions.csv"
)

with st.expander("DCF Assumptions", expanded=True):
    d1, d2, d3, d4 = st.columns(4)

    nke_price = d1.number_input(
        "Reference NKE price ($)",
        value=40.81,
        step=0.10,
    )

    rf = d2.number_input(
        "Risk-free rate",
        value=0.0425,
        format="%.4f",
    )

    beta = d3.number_input(
        "Beta",
        value=1.05,
        step=0.05,
    )

    erp = d4.number_input(
        "Equity risk premium",
        value=0.0500,
        format="%.4f",
    )

    d5, d6, d7 = st.columns(3)

    cod = d5.number_input(
        "Pre-tax cost of debt",
        value=0.0450,
        format="%.4f",
    )

    terminal_g = d6.number_input(
        "Terminal growth",
        value=0.0250,
        format="%.4f",
    )

    tax = d7.number_input(
        "Normalized tax rate",
        value=0.2100,
        format="%.4f",
    )

forecast = build_nike_forecast(
    nike_hist,
    nike_ass,
)

shares = float(nike_hist.iloc[-1]["Diluted Shares"])
debt = float(nike_hist.iloc[-1]["Debt"])

cash = float(
    nike_hist.iloc[-1]["Cash"]
    + nike_hist.iloc[-1]["Short-Term Investments"]
)

net_debt = debt - cash
market_equity = nke_price * shares

dcf_wacc = calc_dcf_wacc(
    rf,
    beta,
    erp,
    cod,
    tax,
    market_equity,
    debt,
)

if dcf_wacc <= terminal_g:
    st.error(
        "DCF cannot be calculated because WACC must exceed "
        "the terminal growth rate."
    )
else:
    nike_val = run_company_dcf(
        forecast,
        dcf_wacc,
        terminal_g,
        net_debt,
        shares,
    )

    v1, v2, v3, v4 = st.columns(4)

    v1.metric(
        "WACC",
        f"{dcf_wacc:.2%}",
    )

    v2.metric(
        "Enterprise Value",
        f"${nike_val['enterprise_value'] / 1000:,.1f}B",
    )

    v3.metric(
        "Implied Share Price",
        f"${nike_val['implied_share_price']:.2f}",
    )

    implied_upside = (
        nike_val["implied_share_price"] / nke_price - 1
    )

    v4.metric(
        "Upside / (Downside)",
        f"{implied_upside:.1%}",
    )

    st.subheader("Historical Actuals & Forecast")

    hist_show = nike_hist[
        [
            "Year",
            "Revenue",
            "EBIT",
            "EBIT Margin",
            "D&A",
            "Capex",
            "Operating NWC",
        ]
    ].copy()

    hist_show["Type"] = "Actual"

    fc_show = forecast[
        [
            "Year",
            "Revenue",
            "EBIT",
            "EBIT Margin",
            "D&A",
            "Capex",
            "Operating NWC",
        ]
    ].copy()

    fc_show["Type"] = "Forecast"

    combined_financials = pd.concat(
        [hist_show, fc_show],
        ignore_index=True,
    )

    st.dataframe(
        combined_financials,
        hide_index=True,
        width="stretch",
    )

    st.subheader("DCF Cash Flow")

    dcf_cash_flow = nike_val["forecast"][
        [
            "Year",
            "Revenue",
            "EBIT",
            "Change in NWC",
            "UFCF",
            "PV UFCF",
        ]
    ].copy()

    st.dataframe(
        dcf_cash_flow,
        hide_index=True,
        width="stretch",
    )

    st.subheader("WACC / Terminal Growth Sensitivity")

    waccs = [
        dcf_wacc - 0.02,
        dcf_wacc - 0.01,
        dcf_wacc,
        dcf_wacc + 0.01,
        dcf_wacc + 0.02,
    ]

    growths = [
        0.015,
        0.020,
        0.025,
        0.030,
        0.035,
    ]

    valid_waccs = [
        w for w in waccs if w > max(growths)
    ]

    if not valid_waccs:
        st.warning(
            "Sensitivity table unavailable because the selected "
            "WACC range does not remain above terminal growth."
        )
    else:
        dcf_sens = dcf_sensitivity(
            forecast,
            net_debt,
            shares,
            valid_waccs,
            growths,
        )

        dcf_sens.index = [
            f"{x:.1%}" for x in dcf_sens.index
        ]

        dcf_sens.columns = [
            f"{x:.1%}" for x in dcf_sens.columns
        ]

        st.dataframe(
            dcf_sens.style.format("${:,.2f}"),
            width="stretch",
        )

    st.caption(
        "Historical financials are sourced from NIKE's FY2026 and "
        "FY2025 SEC filings. Forecast growth, margins, WACC inputs, "
        "and terminal growth are project assumptions, not company guidance "
        "or investment advice."
    )

# ============================================================
# METHODOLOGY & LIMITATIONS
# ============================================================

st.divider()

with st.expander("Methodology & Limitations"):
    start = current["prices"].index.min().strftime("%Y-%m-%d")
    end = current["prices"].index.max().strftime("%Y-%m-%d")

    st.markdown(
        f"""
**Portfolio analysis period:** {start} to {end}

### Portfolio Sleeves
- VTI — US equity
- VXUS — international equity
- AGG — US investment-grade bonds
- SGOV — short-term US Treasuries

### Portfolio Benchmark
- 60% VTI / 40% AGG

### Portfolio Metrics
- Annualized return
- Annualized volatility
- Sharpe ratio
- Maximum drawdown
- Beta vs. 60/40 benchmark

### Illustrative Portfolio Controls
- Portfolio weights = 100%
- Single holding <= 50%
- Total equity <= 80%
- International equity >= 10%
- Short-term Treasury allocation >= 5%
- Annualized volatility <= 20%
- Historical maximum drawdown <= 25%

### NFR Categories
- Operational risk
- Data risk
- Model risk
- Technology risk
- Third-party risk

### NFR Framework Components
- RCSA-style inherent and residual risk scoring
- Preventive/detective control classification
- Automated/semi-automated control classification
- Project-defined KRIs
- Incident and issue logging
- Recurrence and trend analysis

### Company Valuation
- NIKE FY2024–FY2026 historical financials
- 2027E–2031E forecast assumptions
- UFCF
- CAPM cost of equity
- After-tax cost of debt
- WACC
- Gordon Growth terminal value
- Enterprise-to-equity bridge
- Implied share price
- WACC / terminal-growth sensitivity

### Important Limitations
- Historical performance does not predict future performance.
- ETF inception dates limit common-history analysis.
- Historical stress testing uses disclosed proxies where required.
- Sensitivity analysis is illustrative and not an investment recommendation.
- Portfolio-control thresholds are project-defined investment-policy rules,
  not regulatory requirements.
- The NFR section is an educational framework and not a bank's proprietary
  methodology.
- NIKE forecast assumptions are project assumptions and not company guidance.
- The DCF is an educational valuation case study and not investment advice.
"""
    )

st.caption(
    "Portfolio Pulse is an educational analytics, valuation, and risk-controls "
    "project and does not provide personalized investment advice."
)
