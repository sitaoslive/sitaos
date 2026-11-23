import pytest
from server import (
    health,
    get_metrics,
    get_products,
    get_prospects,
    get_agents,
    get_pipeline,
    get_demo_sessions,
    get_workflows,
    get_compliance,
    render_vet_life_demo,
    render_service_os_demo,
    render_onboarding_portal,
    render_command_center,
    get_commercial_workflows,
    run_commercial_cycle,
    get_commercial_telemetry,
    get_financial_model
)

def test_endpoint_health():
    res = health()
    assert res["status"] == "HEALTHY"
    assert "Alpha Vision" in res["system"]

def test_endpoint_metrics():
    res = get_metrics()
    assert res["mrr_usd"] > 0
    assert res["gross_margin_pct"] >= 85.0
    assert "active_subscriptions" in res

def test_endpoint_products():
    res = get_products()
    assert "vet_freedom_os" in res
    assert "service_business_os" in res
    assert res["vet_freedom_os"]["readiness_status"] == "SALES_READY"

def test_endpoint_prospects():
    res = get_prospects()
    assert len(res) >= 2

def test_endpoint_agents():
    res = get_agents()
    assert len(res["agents"]) == 14

def test_endpoint_pipeline():
    res = get_pipeline()
    assert len(res["stages"]) == 18
    assert len(res["contacts"]) >= 2

def test_endpoint_demo_sessions():
    res = get_demo_sessions()
    assert len(res) >= 2

def test_endpoint_workflows():
    res = get_workflows()
    assert res["workflow_count"] == 50

def test_endpoint_compliance():
    res = get_compliance()
    assert "kill_switch_active" in res
    assert res["suppression_count"] >= 2

def test_render_vet_demo_html():
    html = render_vet_life_demo("d_vet_demo_master")
    assert "Vet Freedom OS" in html
    assert "Rastreo GPS" in html

def test_render_service_os_demo_html():
    html = render_service_os_demo("d_ser_demo_master")
    assert "Alpha Service Business OS" in html
    assert "Live Dispatch Radar" in html

def test_render_onboarding_portal_html():
    html = render_onboarding_portal("cust_apex_climate_hvac")
    assert "Welcome to Your Operating Platform" in html
    assert "Book Your 1-on-1 Session" in html

def test_render_command_center_html():
    html = render_command_center()
    assert "Alpha Vision AI Sales OS" in html
    assert "Executive Command Center" in html

def test_endpoint_commercial_workflows():
    res = get_commercial_workflows()
    assert res["total_workflows"] == 35
    assert res["workflows"][0]["ID"] == "WF-001"

def test_endpoint_commercial_telemetry_and_run_cycle():
    tel = run_commercial_cycle()
    assert tel["status"] == "COMPLETED"
    assert tel["prospects_discovered"] >= 1
    assert tel["leads_qualified_high_intent"] >= 1
    
    t_status = get_commercial_telemetry()
    assert t_status["cycle_count"] >= 1
    assert t_status["last_cycle"]["status"] == "COMPLETED"

def test_endpoint_financial_model():
    model = get_financial_model()
    assert model["target_net_profit_monthly_usd"] == 50000.0
    assert model["scenarios"]["base_case"]["net_operating_profit_usd"] == 50000.0
    assert model["hvac_roi_benchmark"]["roi_multiple"] > 10.0
