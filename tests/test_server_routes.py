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
    get_financial_model,
    get_federation_health,
    list_tenants,
    validate_subdomain,
    provision_tenant,
    get_audit_logs,
    submit_engineering_task,
    list_engineering_tasks,
    EngineeringTaskSubmit
)
from engine.db_federation import TenantProvisionRequest

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

def test_endpoint_federation_health():
    res = get_federation_health()
    assert res["overall_status"] == "HEALTHY"
    assert "core_db" in res["databases"]
    assert "vet_db" in res["databases"]

def test_endpoint_list_tenants():
    res = list_tenants()
    assert res["count"] >= 4
    assert len(res["tenants"]) >= 4

def test_endpoint_validate_subdomain():
    valid_res = validate_subdomain("new-clinic-alpha")
    assert valid_res["valid"] is True
    
    reserved_res = validate_subdomain("admin")
    assert reserved_res["valid"] is False

def test_endpoint_provision_tenant():
    req = TenantProvisionRequest(
        business_name="Austin Precision HVAC",
        product_id="service_business_os",
        plan_id="service_growth",
        target_subdomain="austinprecisionhvac",
        owner_name="Dave Miller",
        owner_email="dave@austinprecisionhvac.com",
        owner_phone="+15125550999"
    )
    res = provision_tenant(req)
    assert res["success"] is True
    assert res["subdomain"] == "austinprecisionhvac"
    assert res["status"] == "ACTIVE"

def test_endpoint_audit_logs():
    res = get_audit_logs()
    assert res["count"] >= 1
    assert "logs" in res

def test_endpoint_engineering_tasks():
    req = EngineeringTaskSubmit(
        title="Verify Stripe production webhook signature parsing",
        description="Verify handling of test and live signatures.",
        category="INTEGRATION",
        priority="P1_HIGH"
    )
    res = submit_engineering_task(req)
    assert res["success"] is True
    assert res["task"]["title"] == "Verify Stripe production webhook signature parsing"
    
    tasks = list_engineering_tasks()
    assert tasks["count"] >= 1

