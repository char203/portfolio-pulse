import pandas as pd
from nike_dcf import build_nike_forecast,wacc,dcf,sensitivity

hist=pd.read_csv("valuation_data/nike_historicals.csv")
ass=pd.read_csv("valuation_data/nike_forecast_assumptions.csv")
forecast=build_nike_forecast(hist,ass)

# Project assumptions, not Nike-reported facts.
CURRENT_PRICE=40.81   # Aug. 21, 2026 close derived from $40.26 open and +1.37% day move; update if desired.
RISK_FREE=0.0425
BETA=1.05
ERP=0.050
PRETAX_COST_DEBT=0.045
TAX_RATE=0.21
TERMINAL_GROWTH=0.025

shares=float(hist.iloc[-1]["Diluted Shares"])
debt=float(hist.iloc[-1]["Debt"])
cash=float(hist.iloc[-1]["Cash"]+hist.iloc[-1]["Short-Term Investments"])
net_debt=debt-cash
market_equity=CURRENT_PRICE*shares

w=wacc(RISK_FREE,BETA,ERP,PRETAX_COST_DEBT,TAX_RATE,market_equity,debt)
result=dcf(forecast,w,TERMINAL_GROWTH,net_debt,shares)

print("\nNIKE DCF — PORTFOLIO PULSE")
print("="*70)
print(f"Reference share price: ${CURRENT_PRICE:.2f}")
print(f"WACC: {w:.2%}")
print(f"Terminal growth: {TERMINAL_GROWTH:.2%}")
print(f"Net debt / (net cash): ${net_debt:,.0f}mm")
print(f"Enterprise value: ${result['enterprise_value']:,.0f}mm")
print(f"Equity value: ${result['equity_value']:,.0f}mm")
print(f"Implied share price: ${result['implied_share_price']:.2f}")
print(f"Implied upside/(downside): {result['implied_share_price']/CURRENT_PRICE-1:.1%}")

print("\nHISTORICAL ACTUALS ($mm)")
print(hist[["Year","Revenue","Gross Profit","EBIT","EBIT Margin","D&A","Capex","Operating NWC"]].to_string(index=False))

print("\nFORECAST ($mm)")
print(result["forecast"][["Year","Revenue","Revenue Growth","EBIT Margin","EBIT","D&A","Capex","Change in NWC","UFCF","PV UFCF"]].to_string(index=False))

waccs=[w-.02,w-.01,w,w+.01,w+.02]
gs=[.015,.020,.025,.030,.035]
print("\nIMPLIED SHARE PRICE SENSITIVITY")
print(sensitivity(forecast,net_debt,shares,waccs,gs).round(2).to_string())
