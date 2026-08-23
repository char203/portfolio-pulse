from controls import evaluate_portfolio_controls, controls_summary


def test_base_portfolio_controls_evaluate():
    weights = {
        "VTI": 0.45,
        "VXUS": 0.20,
        "AGG": 0.30,
        "SGOV": 0.05,
    }

    results = evaluate_portfolio_controls(
        weights=weights,
        annualized_volatility=0.1112,
        max_drawdown=-0.2165,
    )

    summary = controls_summary(results)

    assert summary["total_controls"] == 7
    assert summary["failed"] == 0
    assert summary["overall_status"] == "PASS"


def test_control_exception_is_flagged():
    weights = {
        "VTI": 0.70,
        "VXUS": 0.15,
        "AGG": 0.10,
        "SGOV": 0.05,
    }

    results = evaluate_portfolio_controls(
        weights=weights,
        annualized_volatility=0.22,
        max_drawdown=-0.30,
    )

    failed = [r.control for r in results if r.status == "FAIL"]

    assert "Single-Asset Concentration" in failed
    assert "Equity Allocation" in failed
    assert "Portfolio Volatility Limit" in failed
    assert "Maximum Drawdown Limit" in failed
