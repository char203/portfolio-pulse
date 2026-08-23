import streamlit as st
import pandas as pd

from market_engine import run_current_analysis, run_stress_tests
from attribution import calculate_daily_contributions, summarize_contributions
from sensitivity import build_sensitivity_scenarios, sensitivity_table
from controls import evaluate_portfolio_controls, controls_summary

st.set_page_config(
    page_title="Portfolio Pulse",
    page_icon="📈",
    layout="wide",
)

st.title("Portfolio Pulse")
st.caption("Interactive multi-asset portfolio & risk analytics")

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

# -------------------------------------------------------------------
# Portfolio snapshot
# -------------------------------------------------------------------

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

# -------------------------------------------------------------------
# Investment-policy controls
# -------------------------------------------------------------------

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

# -------------------------------------------------------------------
# Wealth curve
# -------------------------------------------------------------------

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

# -------------------------------------------------------------------
# Stress tests
# -------------------------------------------------------------------

st.divider()
st.subheader("Historical Stress Tests")

stress_display = stress[
    ["scenario", "period_return", "max_drawdown", "recovery_date"]
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
    "Historical scenarios describe how the selected allocation behaved in prior market environments. "
    "They are not forecasts."
)

# -------------------------------------------------------------------
# Attribution
# -------------------------------------------------------------------

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

# -------------------------------------------------------------------
# Sensitivity
# -------------------------------------------------------------------

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

sens_display["Sharpe"] = sens_display["Sharpe"].map(lambda x: f"{x:.2f}")
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
    "Sensitivity scenarios apply controlled ±5% and ±10% shifts between VTI and AGG while holding other sleeves constant."
)

# -------------------------------------------------------------------
# Methodology
# -------------------------------------------------------------------

st.divider()

with st.expander("Methodology & limitations"):
    start = current["prices"].index.min().strftime("%Y-%m-%d")
    end = current["prices"].index.max().strftime("%Y-%m-%d")

    st.markdown(
        f"""
**Analysis period:** {start} to {end}

**Current portfolio sleeves**
- VTI — US equity
- VXUS — international equity
- AGG — US investment-grade bonds
- SGOV — short-term US Treasuries

**Benchmark**
- 60% VTI / 40% AGG

**Core metrics**
- Annualized return
- Annualized volatility
- Sharpe ratio
- Maximum drawdown
- Beta vs. 60/40 benchmark

**Illustrative portfolio controls**
- Portfolio weights = 100%
- Single holding <= 50%
- Total equity <= 80%
- International equity >= 10%
- Short-term Treasury allocation >= 5%
- Annualized volatility <= 20%
- Historical maximum drawdown <= 25%

**Important limitations**
- Historical results do not predict future performance.
- ETF inception dates limit common-history analysis.
- Historical stress testing uses disclosed proxies where required.
- Sensitivity analysis is illustrative and not an investment recommendation.
- Portfolio-control thresholds are project-defined investment-policy rules, not regulatory requirements.
"""
    )

st.caption(
    "Portfolio Pulse is an educational analytics project and does not provide personalized investment advice."
)
