# Portfolio Pulse

**Multi-asset portfolio analytics, risk monitoring, and investment-policy controls built with Python, Streamlit, and Excel/VBA.**

## Live Demo

**[Launch Portfolio Pulse →](https://charlottekwon-portfolio-pulse.streamlit.app/)**

Portfolio Pulse is an interactive portfolio analytics platform for evaluating how asset-allocation decisions affect historical return, risk, downside exposure, and benchmark-relative performance.

The project combines:

- Python portfolio analytics
- Interactive Streamlit analysis
- Excel/VBA reporting and automation
- Historical stress testing
- Return attribution with reconciliation controls
- Allocation sensitivity analysis
- Investment-policy controls and exception monitoring
- Automated testing

---

## Demo

### Portfolio Overview

![Portfolio Pulse overview](assets/portfolio-overview.png)

### Historical Risk Analysis

![Portfolio Pulse stress testing](assets/stress-testing.png)

### Attribution & Allocation Sensitivity

![Portfolio Pulse allocation analysis](assets/allocation-analysis.png)

---

## What Portfolio Pulse Does

Users define a hypothetical portfolio allocation across four asset sleeves:

| ETF | Exposure |
|---|---|
| VTI | U.S. equities |
| VXUS | International equities |
| AGG | U.S. investment-grade bonds |
| SGOV | Short-term U.S. Treasuries |

Portfolio Pulse evaluates the allocation against a **60% VTI / 40% AGG benchmark**.

The analytics engine calculates:

- Annualized return
- Annualized volatility
- Sharpe ratio
- Maximum drawdown
- Beta versus the 60/40 benchmark
- Ending portfolio value
- Historical wealth curves
- Historical crisis performance
- Asset-level return contribution
- Allocation sensitivity
- Investment-policy control exceptions

The same Python analytics engine supports both the Streamlit application and the Excel/VBA workflow.

---

## Why I Built It

I built Portfolio Pulse to develop a more hands-on understanding of portfolio construction and risk analysis beyond standard finance coursework.

The initial question was:

> How can portfolio analytics be rigorous enough to support an investment decision while still being understandable to a non-specialist?

That led to a system designed around three principles:

1. **Measure both return and risk.**  
   Portfolio performance is evaluated alongside volatility, drawdown, beta, and historical crisis behavior.

2. **Make assumptions explicit.**  
   Historical proxy substitutions and portfolio-control thresholds are disclosed rather than hidden.

3. **Separate analytics from presentation.**  
   Python remains the calculation source of truth while Streamlit and Excel/VBA provide different interfaces to the same analytical workflow.

---

## Architecture

```text
Market Data
    │
    ▼
  data.py
    │
    ▼
portfolio.py + analytics.py
    │
    ▼
market_engine.py
    │
    ├──────────────► Historical Stress Testing
    │
    ├──────────────► Return Attribution
    │                    │
    │                    └── Reconciliation Control
    │
    ├──────────────► Allocation Sensitivity
    │
    ├──────────────► Investment-Policy Controls
    │                    │
    │                    ▼
    │               PASS / FAIL
    │                    │
    │                    ▼
    │             Exception + Severity
    │                    │
    │                    ▼
    │             Remediation Reporting
    │
    ├──────────────► Streamlit
    │
    └──────────────► Excel / VBA
```

The analytical logic is separated from the user interfaces so calculations remain consistent across outputs.

---

## Portfolio Analytics

### Performance

Portfolio Pulse evaluates historical portfolio performance using:

- annualized return
- ending wealth
- benchmark-relative return

### Risk

Risk analysis includes:

- annualized volatility
- maximum drawdown
- beta versus the 60/40 benchmark
- historical stress scenarios

This allows portfolio decisions to be evaluated based on both the return generated and the risk required to generate it.

---

## Historical Stress Testing

Portfolio Pulse evaluates portfolio behavior during three distinct historical market environments:

### Global Financial Crisis

Captures an equity and credit-market crisis in which portfolio losses and recovery behavior can be evaluated under severe financial stress.

### COVID Shock

Captures the rapid 2020 equity-market selloff and unusually fast subsequent recovery.

### 2022 Inflation / Rate Shock

Captures an environment in which rising inflation and interest rates pressured both equities and duration-sensitive fixed income.

For each scenario, the system evaluates:

- period return
- maximum drawdown
- peak date
- trough date
- recovery date

---

## Historical Proxy Methodology

One practical challenge is that several ETFs in the current portfolio did not exist during earlier market crises.

Portfolio Pulse does **not** silently remove those exposures or pretend that current ETFs have longer histories than they actually do.

Instead, current-fund analysis is separated from historical scenario analysis, and disclosed historical proxies are used where necessary.

Examples include:

```text
VXUS → VEU
SGOV → SHY
```

The application records these substitutions explicitly.

Automated tests also verify that historical proxy resolution does not silently drop an asset from a stress scenario.

---

## Return Attribution

Portfolio Pulse calculates asset-level daily arithmetic contribution as:

```text
Daily Contribution = Portfolio Weight × Asset Daily Return
```

The system then performs a reconciliation check:

```text
Σ Asset Contributions = Portfolio Daily Return
```

This control verifies that the attribution output ties back to the underlying portfolio return.

Multi-period results are therefore described as **cumulative arithmetic contribution**.

The project deliberately does **not** label this analysis as Brinson attribution.

---

## Allocation Sensitivity

Portfolio Pulse evaluates controlled allocation changes around the selected portfolio.

Current scenarios include:

```text
Base Portfolio

5% VTI → AGG
10% VTI → AGG

5% AGG → VTI
10% AGG → VTI
```

For each scenario, the engine recalculates:

- CAGR
- annualized volatility
- Sharpe ratio
- maximum drawdown
- ending portfolio value

The purpose is to make the historical trade-off between additional equity exposure, return potential, and downside risk visible.

---

## Portfolio Controls & Exception Monitoring

Portfolio Pulse also includes an automated **investment-policy controls layer**.

Rather than simply calculating portfolio statistics, this layer translates defined portfolio rules into automated tests.

The workflow is:

```text
Policy Rule
    ↓
Automated Control
    ↓
Portfolio Test
    ↓
PASS / FAIL
    ↓
Exception + Severity
    ↓
Remediation
```

### Current Controls

The default policy evaluates whether:

| Control | Rule |
|---|---|
| Portfolio Weight Total | Weights must equal 100% |
| Single-Asset Concentration | No holding exceeds 50% |
| Equity Allocation | Total equity exposure does not exceed 80% |
| International Diversification | International allocation is at least 10% |
| Liquidity Floor | Short-term Treasury allocation is at least 5% |
| Portfolio Volatility | Annualized volatility does not exceed 20% |
| Maximum Drawdown | Historical maximum drawdown does not exceed 25% |

Each control produces:

- PASS / FAIL status
- severity
- observed value
- policy threshold
- remediation guidance when an exception occurs

For example:

```text
Control: Single-Asset Concentration
Rule: No holding > 50%
Actual: 70%
Status: FAIL
Severity: Medium
Remediation: Reduce concentrated asset exposure.
```

### Important Controls Disclaimer

These thresholds are **project-defined investment-policy rules created for educational analysis**.

They are not regulatory requirements, and Portfolio Pulse should not be interpreted as a regulatory compliance system.

The purpose of this module is to demonstrate how a defined policy can be translated into automated controls, exception detection, and remediation-oriented reporting.

---

## Streamlit Application

The Streamlit interface provides interactive allocation controls and immediately recalculates portfolio analytics.

The application includes:

- portfolio allocation sliders
- portfolio snapshot KPIs
- investment-policy control results
- exception monitoring
- portfolio vs. benchmark wealth curve
- historical stress tests
- return-driver visualization
- allocation sensitivity analysis
- methodology and limitations

Run locally with:

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

---

## Excel + VBA Workflow

Portfolio Pulse also includes an analyst-style Excel implementation.

The Excel workflow supports:

- editable portfolio inputs
- allocation validation
- Python-driven analytics refresh
- portfolio KPIs
- historical stress-test outputs
- wealth-curve visualization
- return attribution
- allocation sensitivity
- automated reporting

VBA provides the interaction and automation layer while Python remains the analytical engine.

This design allows portfolio analysis to be consumed through a familiar spreadsheet workflow without duplicating the underlying financial calculations.

---

## Automated Testing

Portfolio Pulse currently includes **9 automated tests**.

Run them with:

```bash
python3 -m pytest tests -v
```

The test suite covers:

1. Portfolio-weight normalization
2. Weighted portfolio-return calculation
3. Zero-volatility behavior
4. Maximum-drawdown calculation
5. Attribution reconciliation to portfolio return
6. Compliant portfolio-control evaluation
7. Portfolio-control exception detection
8. Historical proxy resolution
9. Prevention of silent asset dropping during proxy resolution

A successful run should return:

```text
9 passed
```

Testing is particularly important for the controls and attribution layers because those features are intended to identify or explain portfolio behavior rather than simply display statistics.

---

## Project Structure

```text
portfolio-pulse/
│
├── app.py
├── analytics.py
├── attribution.py
├── controls.py
├── data.py
├── market_engine.py
├── portfolio.py
├── scenarios.py
├── sensitivity.py
│
├── excel_bidirectional.py
│
├── requirements.txt
├── requirements_streamlit.txt
├── README.md
│
├── tests/
│   ├── test_analytics.py
│   ├── test_attribution.py
│   ├── test_controls.py
│   └── test_data.py
│
├── assets/
│   ├── portfolio-overview.png
│   ├── stress-testing.png
│   └── allocation-analysis.png
│
└── excel/
    ├── Portfolio_Pulse_Analysis.xlsm
    ├── Portfolio_Pulse_Report.pdf
    ├── README_VBA.md
    │
    └── vba/
        ├── AddAttributionChart.bas
        ├── AddSensitivityChart.bas
        ├── AddWealthCurveChart.bas
        ├── BuildDashboard.bas
        ├── GenerateReport.bas
        ├── PortfolioChecks.bas
        ├── RefreshData.bas
        ├── RefreshPortfolio.bas
        ├── ReportGenerator.bas
        ├── StressTesting.bas
        └── ValidatePortfolio.bas
```

---

## Tech Stack

**Finance & Data**

- Python
- pandas
- NumPy
- yfinance

**Application**

- Streamlit

**Spreadsheet Automation**

- Microsoft Excel
- VBA
- openpyxl

**Testing**

- pytest

**Version Control & Deployment**

- Git
- GitHub
- Streamlit Community Cloud

---

## Key Takeaways

Building Portfolio Pulse surfaced several practical lessons about portfolio analysis.

### Diversification is about risk exposure, not asset count

Adding more asset classes does not automatically reduce drawdown. The underlying exposures and their behavior across market regimes matter more than the number of holdings.

### Ending return can hide path risk

Two portfolios can produce similar ending wealth while exposing an investor to very different drawdowns and recovery periods.

### Stock/bond diversification is regime-dependent

The 2022 inflation and rate shock demonstrates that equities and bonds do not necessarily offset one another in every environment.

### Benchmark-relative performance needs risk context

Outperforming a benchmark is more informative when considered alongside volatility, drawdown, beta, and the additional risk required to generate that return.

### Controls make analytical rules operational

A portfolio rule becomes more useful when it can be translated into a testable threshold, evaluated consistently, and surfaced as an exception when breached.

### Reconciliation matters

Analytical outputs should tie back to their underlying calculations. The attribution reconciliation control was added specifically to verify that reported asset contributions reproduce portfolio daily return.

---

## Limitations

Portfolio Pulse is an educational analytics project.

Important limitations include:

- Historical performance does not predict future results.
- The portfolio uses a limited ETF universe.
- ETF inception dates constrain common-history analysis.
- Historical proxies approximate exposures and are not perfect replicas of later ETFs.
- Sharpe-ratio results depend on the selected risk-free-rate methodology.
- Historical stress tests are descriptive, not predictive.
- Sensitivity scenarios are illustrative rather than optimization recommendations.
- Portfolio-control thresholds are project-defined rules, not regulatory requirements.
- Portfolio Pulse does not provide personalized investment advice.

---

## Live Application

**[Launch Portfolio Pulse](https://charlottekwon-portfolio-pulse.streamlit.app/)**

Built as an independent portfolio analytics project using Python, Streamlit, Excel, and VBA.
