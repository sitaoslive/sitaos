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
    EngineeringTaskSubmit,
    get_reddit_metrics,
    list_reddit_communities,
    ingest_reddit_discussion,
    list_reddit_opportunities,
    draft_reddit_answer,
    list_reddit_drafts,
    review_reddit_draft,
    toggle_reddit_emergency_stop,
    RedditIngestRequest,
    RedditDraftRequest,
    RedditReviewRequest,
    RedditEmergencyStopRequest
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

def test_endpoint_reddit_metrics_and_communities():
    metrics = get_reddit_metrics()
    assert "total_discussions_discovered" in metrics
    assert "monitored_communities_count" in metrics

    comms = list_reddit_communities()
    assert comms["count"] >= 5
    assert any(c["name"] == "smallbusiness" for c in comms["communities"])

def test_endpoint_reddit_ingest_and_opportunities():
    req = RedditIngestRequest(
        reddit_post_id="t3_srv001",
        subreddit="smallbusiness",
        title="Server route ingest test for lead conversion",
        excerpt="How to handle sales follow-up and speed to lead."
    )
    res = ingest_reddit_discussion(req)
    assert res["success"] is True

    opps = list_reddit_opportunities()
    assert opps["count"] >= 1
    assert any(c["reddit_post_id"] == "t3_srv001" for c in opps["candidates"])

def test_endpoint_reddit_draft_and_review():
    opps = list_reddit_opportunities()
    cand_id = opps["candidates"][0]["id"]

    draft_req = RedditDraftRequest(candidate_id=cand_id, style="DETAILED_ANSWER")
    draft_res = draft_reddit_answer(draft_req)
    assert draft_res["status"] == "AWAITING_APPROVAL"
    draft_id = draft_res["id"]

    drafts = list_reddit_drafts()
    assert drafts["count"] >= 1

    rev_req = RedditReviewRequest(draft_id=draft_id, action="APPROVE", reviewer="CTO")
    rev_res = review_reddit_draft(rev_req)
    assert rev_res["status"] == "APPROVED_FOR_MANUAL_ACTION"
    assert "clipboard_ready_body" in rev_res

def test_endpoint_reddit_emergency_stop():
    stop_req = RedditEmergencyStopRequest(active=True, reason="Maintenance test")
    res = toggle_reddit_emergency_stop(stop_req)
    assert res["emergency_stop_active"] is True

    restore_req = RedditEmergencyStopRequest(active=False)
    res_restore = toggle_reddit_emergency_stop(restore_req)
    assert res_restore["emergency_stop_active"] is False

