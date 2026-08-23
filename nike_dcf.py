import pandas as pd

def build_nike_forecast(historical, assumptions):
    h = historical.copy()
    a = assumptions.copy()
    base_revenue = float(h.iloc[-1]["Revenue"])
    base_nwc = float(h.iloc[-1]["Operating NWC"])
    rows=[]
    prev_revenue=base_revenue
    prev_nwc=base_nwc
    for _,x in a.iterrows():
        revenue=prev_revenue*(1+x["Revenue Growth"])
        ebit=revenue*x["EBIT Margin"]
        da=revenue*x["D&A % Revenue"]
        capex=revenue*x["Capex % Revenue"]
        nwc=revenue*x["NWC % Revenue"]
        delta_nwc=nwc-prev_nwc
        ufcf=ebit*(1-x["Tax Rate"])+da-capex-delta_nwc
        rows.append({
            "Year":int(x["Year"]),"Revenue":revenue,"Revenue Growth":x["Revenue Growth"],
            "EBIT Margin":x["EBIT Margin"],"EBIT":ebit,"Tax Rate":x["Tax Rate"],
            "D&A":da,"Capex":capex,"Operating NWC":nwc,"Change in NWC":delta_nwc,"UFCF":ufcf
        })
        prev_revenue,prev_nwc=revenue,nwc
    return pd.DataFrame(rows)

def capm_cost_of_equity(rf,beta,erp):
    return rf+beta*erp

def wacc(rf,beta,erp,pretax_cod,tax_rate,equity_value,debt):
    total=equity_value+debt
    if total<=0: raise ValueError("Capital must be positive")
    coe=capm_cost_of_equity(rf,beta,erp)
    at_cod=pretax_cod*(1-tax_rate)
    return equity_value/total*coe + debt/total*at_cod

def dcf(forecast,wacc_rate,g,net_debt,diluted_shares):
    if wacc_rate<=g: raise ValueError("WACC must exceed terminal growth")
    f=forecast.copy()
    f["Period"]=range(1,len(f)+1)
    f["Discount Factor"]=1/(1+wacc_rate)**f["Period"]
    f["PV UFCF"]=f["UFCF"]*f["Discount Factor"]
    tv=f["UFCF"].iloc[-1]*(1+g)/(wacc_rate-g)
    pv_tv=tv*f["Discount Factor"].iloc[-1]
    ev=f["PV UFCF"].sum()+pv_tv
    eq=ev-net_debt
    return {"forecast":f,"terminal_value":tv,"pv_terminal_value":pv_tv,
            "enterprise_value":ev,"equity_value":eq,
            "implied_share_price":eq/diluted_shares}

def sensitivity(forecast,net_debt,shares,waccs,growths):
    out={}
    for g in growths:
        out[g]=[]
        for w in waccs:
            out[g].append(dcf(forecast,w,g,net_debt,shares)["implied_share_price"] if w>g else None)
    return pd.DataFrame(out,index=waccs)
