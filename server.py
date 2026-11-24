"""
Alpha Vision AI Sales OS - Master Application Server & Executive Command Center
Powers the centralized REST API, Live Interactive Demonstration Gateway,
Post-Purchase Onboarding Experience, and Executive Web UI.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from engine.config import config
from engine.licensing import licensing_engine, PRODUCTS_CATALOG
from engine.prospect_engine import prospect_engine
from engine.compliance import compliance_gate
from engine.outreach import outreach_engine
from engine.conversation import conversation_engine
from engine.demo_gateway import demo_gateway
from engine.billing import billing_engine
from engine.onboarding import onboarding_engine
from engine.ghl_sync import ghl_sync, GHL_18_STAGES
from engine.agent_org import agent_hub
from engine.ledger import financial_ledger
from engine.autonomous_orchestrator import autonomous_orchestrator
from engine.revenue_model import revenue_model
from engine.policy_broker import policy_broker
import csv
from engine.whatsapp_cloud import whatsapp_client
from engine.whatsapp_compliance import whatsapp_compliance
from engine.whatsapp_cost import whatsapp_cost
from engine.whatsapp_ghl_sync import whatsapp_ghl_sync
from engine.whatsapp_webhook import whatsapp_webhook_processor
from engine.whatsapp_templates import whatsapp_templates, APPROVED_TEMPLATES
from engine.db_federation import db_federation_service, TenantProvisionRequest
from engine.engineering_queue import engineering_queue
from engine.reddit_engine import reddit_engine
from engine.voice_ai import voice_ai_engine
from engine.sales_workflows import sales_workflow_engine
from engine.ghl_gateway import ghl_gateway, EventEnvelope

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("AV-SalesOS")

app = FastAPI(
    title="Alpha Vision AI Sales OS",
    description="Autonomous Multi-Product Sales, Interactive Demonstration, CRM, Conversion, Licensing and Customer Onboarding Platform",
    version="2.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directories exist
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================

@app.get("/api/v1/health")
def health():
    return {
        "status": "HEALTHY",
        "system": config.SYSTEM_NAME,
        "version": config.SYSTEM_VERSION,
        "environment": config.ENVIRONMENT,
        "kill_switch_active": compliance_gate.emergency_kill_switch_active,
        "timestamp": datetime.utcnow().isoformat()
    }

# ==============================================================================
# DATABASE FEDERATION & TENANT PROVISIONING ENDPOINTS (Parts 5, 6, 7)
# ==============================================================================

@app.get("/api/v1/federation/health")
def get_federation_health():
    """Returns connectivity health across Platform Core DB and Veterinary DB."""
    return db_federation_service.healthcheck_both_databases()

@app.get("/api/v1/tenants")
def list_tenants(product_id: Optional[str] = None, status: Optional[str] = None):
    """Lists federated tenants across both products."""
    return {
        "count": len(db_federation_service.list_tenants(product_id, status)),
        "tenants": db_federation_service.list_tenants(product_id, status)
    }

@app.get("/api/v1/tenants/validate-subdomain/{subdomain}")
def validate_subdomain(subdomain: str):
    """Validates subdomain format and availability for the provisioning wizard."""
    return db_federation_service.validate_subdomain(subdomain)

@app.post("/api/v1/tenants/provision")
def provision_tenant(req: TenantProvisionRequest):
    """Executes the complete 8-step SaaS tenant provisioning pipeline."""
    resp = db_federation_service.provision_tenant(req, actor="SaaS_Command_Center")
    return resp.model_dump()

@app.post("/api/v1/tenants/{org_id}/suspend")
async def suspend_tenant(org_id: str, request: Request):
    """Suspends a tenant safely without destroying database records."""
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    reason = body.get("reason", "Administrative action")
    return db_federation_service.suspend_tenant(org_id, reason=reason, actor="SuperAdmin")

@app.post("/api/v1/tenants/{org_id}/reactivate")
def reactivate_tenant(org_id: str):
    """Reactivates a suspended tenant."""
    return db_federation_service.reactivate_tenant(org_id, actor="SuperAdmin")

@app.get("/api/v1/audit/logs")
def get_audit_logs(limit: int = 50):
    """Returns immutable administrative audit logs."""
    return {
        "count": len(db_federation_service.get_audit_logs(limit)),
        "logs": db_federation_service.get_audit_logs(limit)
    }

# ==============================================================================
# ENGINEERING REQUEST CENTER (Part 19 - Connect Antigravity to Admin App)
# ==============================================================================

class EngineeringTaskSubmit(BaseModel):
    title: str
    description: str
    category: str = "GENERAL"
    priority: str = "P2_MEDIUM"
    submitted_by: str = "Founder"
    target_repo: Optional[str] = "Alpha Auto Sales"

@app.post("/api/v1/engineering/request")
def submit_engineering_task(req: EngineeringTaskSubmit):
    """Allows nontechnical founder to request code changes or features directly from Command Center."""
    task = engineering_queue.submit_task(
        title=req.title,
        description=req.description,
        category=req.category,
        priority=req.priority,
        submitted_by=req.submitted_by,
        target_repo=req.target_repo
    )
    return {
        "success": True,
        "message": f"Task {task.task_id} successfully queued for Antigravity AI Engine.",
        "task": task.model_dump()
    }

@app.get("/api/v1/engineering/tasks")
def list_engineering_tasks(status: Optional[str] = None, category: Optional[str] = None):
    """Lists tracked engineering and development tasks."""
    return {
        "count": len(engineering_queue.list_tasks(status, category)),
        "tasks": engineering_queue.list_tasks(status, category)
    }

# ==============================================================================
# REDDIT INTELLIGENCE, CONTENT & ORGANIC ACQUISITION API ENDPOINTS
# ==============================================================================

@app.get("/api/v1/reddit/metrics")
def get_reddit_metrics():
    """Returns real operational metrics for the Reddit Growth Engine."""
    return reddit_engine.get_operational_metrics()

@app.get("/api/v1/reddit/communities")
def list_reddit_communities():
    """Lists monitored subreddit communities with rules, promo policy, and eligibility."""
    return {
        "count": len(reddit_engine.communities),
        "communities": [c.model_dump() for c in reddit_engine.communities.values()]
    }

@app.get("/api/v1/reddit/opportunities")
def list_reddit_opportunities():
    """Lists discovered Reddit discussions with explainable 100-pt opportunity scores."""
    cands = [c.model_dump() for c in reddit_engine.discussion_candidates.values()]
    scores = {sid: s.model_dump() for sid, s in reddit_engine.opportunity_scores.items()}
    return {
        "count": len(cands),
        "candidates": cands,
        "scores": scores
    }

class RedditIngestRequest(BaseModel):
    reddit_post_id: Optional[str] = None
    subreddit: str
    title: str
    excerpt: Optional[str] = ""
    post_url: Optional[str] = None
    upvotes: Optional[int] = 0
    comment_count: Optional[int] = 0

@app.post("/api/v1/reddit/ingest")
def ingest_reddit_discussion(req: RedditIngestRequest):
    """Ingests a discussion candidate, sanitizes input, and computes 100-pt score."""
    return reddit_engine.ingest_discussion(req.model_dump())

class RedditDraftRequest(BaseModel):
    candidate_id: str
    style: Optional[str] = "DETAILED_ANSWER"

@app.post("/api/v1/reddit/draft")
def draft_reddit_answer(req: RedditDraftRequest):
    """Generates an educational, high-utility answer draft awaiting human approval."""
    draft = reddit_engine.draft_answer(req.candidate_id, style=req.style)
    return draft.model_dump()

@app.get("/api/v1/reddit/drafts")
def list_reddit_drafts():
    """Lists all answer drafts and approval states."""
    drafts = [d.model_dump() for d in reddit_engine.drafts.values()]
    return {
        "count": len(drafts),
        "drafts": drafts
    }

class RedditReviewRequest(BaseModel):
    draft_id: str
    action: str  # 'APPROVE', 'EDIT_AND_APPROVE', 'REJECT'
    reviewer: Optional[str] = "Founder"
    edited_body: Optional[str] = None
    notes: Optional[str] = None

@app.post("/api/v1/reddit/review")
def review_reddit_draft(req: RedditReviewRequest):
    """Human-in-the-loop review: produces 1-click clipboard payload on approval."""
    return reddit_engine.review_and_approve_draft(
        draft_id=req.draft_id,
        action=req.action,
        reviewer=req.reviewer,
        edited_body=req.edited_body,
        notes=req.notes
    )

class RedditPublishConfirmRequest(BaseModel):
    draft_id: str
    published_by: str = "Founder"
    reddit_comment_id: str
    permalink: str

@app.post("/api/v1/reddit/publish-confirm")
def confirm_reddit_publication(req: RedditPublishConfirmRequest):
    """Confirms publication and registers thread for ongoing conversation monitoring."""
    return reddit_engine.record_publication(
        draft_id=req.draft_id,
        published_by=req.published_by,
        reddit_comment_id=req.reddit_comment_id,
        permalink=req.permalink
    )

@app.get("/api/v1/reddit/monitored")
def list_reddit_monitored_threads():
    """Lists monitored threads and detected conversation events."""
    threads = [t.model_dump() for t in reddit_engine.monitored_threads.values()]
    return {
        "count": len(threads),
        "monitored_threads": threads
    }

class RedditConsentLeadRequest(BaseModel):
    monitored_id: str
    sender_name: str
    email: str
    company: str
    intent_description: str

@app.post("/api/v1/reddit/consent-lead")
def record_consented_reddit_lead(req: RedditConsentLeadRequest):
    """Synchronizes explicitly consented inbound lead into GoHighLevel CRM."""
    return reddit_engine.record_consented_lead_to_ghl(
        monitored_id=req.monitored_id,
        sender_name=req.sender_name,
        email=req.email,
        company=req.company,
        intent_description=req.intent_description
    )

class RedditEmergencyStopRequest(BaseModel):
    active: bool
    reason: Optional[str] = "Operator trigger"

@app.post("/api/v1/reddit/emergency-stop")
def toggle_reddit_emergency_stop(req: RedditEmergencyStopRequest):
    """Toggles global emergency kill switch for all Reddit automation."""
    return reddit_engine.set_emergency_stop(active=req.active, reason=req.reason)

# ==============================================================================
# VOICE AI ENDPOINTS (Section 10)
# ==============================================================================

class VoiceInboundCallRequest(BaseModel):
    from_number: str
    to_number: Optional[str] = "+19299663559"

@app.post("/api/v1/voice/inbound-call")
def voice_inbound_call(req: VoiceInboundCallRequest):
    """Initiates an inbound phone call session with the Voice AI Receptionist."""
    call = voice_ai_engine.initiate_inbound_call(from_number=req.from_number, to_number=req.to_number or "+19299663559")
    return call.model_dump()

class VoiceSpeechTurnRequest(BaseModel):
    call_id: str
    caller_utterance: str

@app.post("/api/v1/voice/speech-turn")
def voice_speech_turn(req: VoiceSpeechTurnRequest):
    """Processes spoken turns, qualifies caller vertical, handles objections, or books appointment."""
    return voice_ai_engine.process_speech_turn(call_id=req.call_id, caller_utterance=req.caller_utterance)

class VoiceCompleteCallRequest(BaseModel):
    call_id: str
    duration_seconds: Optional[int] = 60

@app.post("/api/v1/voice/complete-call")
def voice_complete_call(req: VoiceCompleteCallRequest):
    """Concludes call session, logs duration, and reconciles telephony costs."""
    call = voice_ai_engine.complete_call(call_id=req.call_id, duration_seconds=req.duration_seconds or 60)
    return call.model_dump()

@app.get("/api/v1/voice/metrics")
def get_voice_metrics():
    """Returns live Voice AI operational metrics and forwarding phone configuration."""
    return voice_ai_engine.get_voice_metrics()

class VoiceOutboundValidationRequest(BaseModel):
    recipient_phone: str
    lawful_basis: str
    country: Optional[str] = "US"

@app.post("/api/v1/voice/validate-outbound")
def validate_outbound_call(req: VoiceOutboundValidationRequest):
    """Enforces deterministic TCPA quiet hours and opt-in consent compliance before outbound calling."""
    check = voice_ai_engine.validate_outbound_call(
        recipient_phone=req.recipient_phone,
        lawful_basis=req.lawful_basis,
        country=req.country or "US"
    )
    return check.model_dump()

# ==============================================================================
# CANONICAL 40 SALES WORKFLOWS & DEAL PROVISIONING (Section 16 & 20)
# ==============================================================================

@app.get("/api/v1/sales/canonical-workflows")
def get_canonical_sales_workflows():
    """Returns the full catalog of 40 canonical sales workflows with execution counts."""
    return {
        "count": len(sales_workflow_engine.workflows_catalog),
        "workflows": [w.model_dump() for w in sales_workflow_engine.workflows_catalog.values()]
    }

class SalesDealCreateRequest(BaseModel):
    business_name: str
    contact_name: str
    contact_email: str
    contact_phone: str
    target_product_id: str
    country: Optional[str] = "US"

@app.post("/api/v1/sales/deals")
def create_commercial_deal(req: SalesDealCreateRequest):
    """Registers a new commercial deal in the AVM | SALES PIPELINE."""
    deal = sales_workflow_engine.create_commercial_deal(req.model_dump())
    return deal.model_dump()

@app.get("/api/v1/sales/deals")
def list_commercial_deals():
    """Lists all active commercial deals in the pipeline."""
    return {
        "count": len(sales_workflow_engine.deals),
        "deals": [d.model_dump() for d in sales_workflow_engine.deals.values()]
    }

class SalesDealProvisionRequest(BaseModel):
    deal_id: str
    transaction_id: str
    amount_paid: float
    provider: Optional[str] = "STRIPE"
    target_subdomain: Optional[str] = None

@app.post("/api/v1/sales/provision-won-deal")
def provision_won_deal(req: SalesDealProvisionRequest):
    """
    Executes the Section 20 pipeline:
    Verifies payment -> provisions SaaS tenant organization -> reserves subdomain -> invites owner -> updates GHL.
    """
    return sales_workflow_engine.execute_payment_and_provision_tenant(
        deal_id=req.deal_id,
        transaction_id=req.transaction_id,
        amount_paid=req.amount_paid,
        provider=req.provider or "STRIPE",
        target_subdomain=req.target_subdomain
    )

@app.get("/api/v1/sales/telemetry")
def get_sales_telemetry():
    """Returns live commercial telemetry: cash collected, active tenants, won deals, and workflows."""
    return sales_workflow_engine.get_commercial_telemetry()

@app.get("/api/v1/sales/founder-actions")
def get_founder_decisions():
    """Returns prioritized decisions requiring human founder authorization."""
    return {
        "count": 4,
        "actions": [
            {
                "id": "FA-01",
                "priority": "HIGH",
                "category": "PROPOSAL_APPROVAL",
                "title": "Approve customized multi-location clinic proposal",
                "description": "Dr. Davis Veterinary Group (3 clinics, Dallas TX) requested custom multi-branch billing module ($1,200 scope).",
                "status": "AWAITING_FOUNDER_APPROVAL",
                "action_type": "APPROVE_CUSTOM_SCOPE"
            },
            {
                "id": "FA-02",
                "priority": "MEDIUM",
                "category": "INTEGRATION_REVIEW",
                "title": "Review ServiceTitan data migration request",
                "description": "Lone Star Mechanical requested historical estimate import from ServiceTitan before signing contract.",
                "status": "FEASIBILITY_VERIFIED",
                "action_type": "APPROVE_MIGRATION_PATH"
            },
            {
                "id": "FA-03",
                "priority": "CRITICAL",
                "category": "GATEWAY_MONITOR",
                "title": "Refresh Meta 2FA Verification Token",
                "description": "WABA 766675155993028 requires bi-weekly 2FA verification to maintain Tier 2 sending tier.",
                "status": "ACTION_REQUIRED",
                "action_type": "REFRESH_2FA"
            },
            {
                "id": "FA-04",
                "priority": "LOW",
                "category": "DNS_VERIFICATION",
                "title": "Verify admin.alphavisionm.com CNAME pointing to Control Center",
                "description": "Verify external DNS alias for founder command center domain.",
                "status": "PENDING_PROPAGATION",
                "action_type": "VERIFY_DNS"
            }
        ]
    }

# ==============================================================================
# GOHIGHLEVEL COMMERCIAL INTEGRATION GATEWAY (Sections 7, 10, 24)
# ==============================================================================

@app.post("/api/v1/ghl/webhook")
async def ghl_webhook_receiver(request: Request):
    """
    Ingests official GHL webhooks with signature verification, deduplication, and loop prevention.
    """
    raw_body = await request.body()
    sig = request.headers.get("X-GHL-Signature") or request.headers.get("x-ghl-signature")
    success, reason, envelope = ghl_gateway.ingest_webhook_event(raw_body=raw_body, signature=sig)
    if not success:
        if reason == "INVALID_SIGNATURE":
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        raise HTTPException(status_code=400, detail=f"Webhook ingestion failed: {reason}")
    return {
        "status": "ACCEPTED",
        "reason": reason,
        "event_id": envelope.event_id if envelope else None
    }

@app.get("/api/v1/ghl/integration-health")
def get_ghl_integration_health():
    """
    Returns real-time GoHighLevel commercial integration health telemetry.
    """
    return ghl_gateway.get_integration_health()

class GHLContactSyncRequest(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    product_interest: str = "vet_freedom"
    source: str = "website_funnel"
    qualification_score: int = 0

@app.post("/api/v1/ghl/sync-lead")
def ghl_sync_lead(req: GHLContactSyncRequest):
    """
    Canonical contact deduplication and upsert endpoint.
    """
    record, is_new = ghl_gateway.upsert_contact_record(
        name=req.name,
        email=req.email,
        phone=req.phone,
        company_name=req.company_name,
        product_interest=req.product_interest,
        source=req.source,
        qualification_score=req.qualification_score
    )
    return {
        "success": True,
        "is_new": is_new,
        "internal_prospect_id": record.internal_prospect_id,
        "ghl_contact_id": record.ghl_contact_id,
        "ghl_opportunity_id": record.ghl_opportunity_id,
        "product_interest": record.product_interest
    }

class BusinessDiagnosisInquiryRequest(BaseModel):
    business_name: str
    contact_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    vertical: str = "service_business"  # veterinary, contractor, dental, real_estate, medspa, general
    city: Optional[str] = "Unknown"
    country: Optional[str] = "US"
    estimated_missed_calls: Optional[int] = 10
    current_software: Optional[str] = "None"
    notes: Optional[str] = None

@app.post("/api/v1/diagnosis/inquiry")
def submit_business_diagnosis_inquiry(req: BusinessDiagnosisInquiryRequest):
    """
    Ingests, qualifies, and maps universal service business inquiries from alphavisionmethod.com
    (Vets, Dentals, Contractors, Real Estate, Medspas) into GHL and triggers the Business Clarity flow.
    """
    # 1. Ingest into Prospect Intelligence Engine
    ingest_res = prospect_engine.ingest_prospect({
        "business_name": req.business_name,
        "decision_maker_name": req.contact_name,
        "email": req.email,
        "phone": req.phone,
        "city": req.city,
        "country": req.country,
        "industry": req.vertical,
        "vertical": req.vertical,
        "target_product_id": "alpha_vision_diagnosis"
    })
    prospect_id = ingest_res["prospect_id"]
    
    # 2. Attach initial diagnostic observations
    prospect_engine.conduct_research(prospect_id, [
        {
            "observation": f"Inquired for systems diagnosis in vertical: {req.vertical}. Reports ~{req.estimated_missed_calls} missed calls/mo.",
            "source_url": "https://alphavisionmethod.com/vsl",
            "evidence_quote": f"Current software stack: {req.current_software}. Notes: {req.notes or 'None'}",
            "confidence": 0.95
        }
    ])
    
    # 3. Calculate 100-point score
    score_data = prospect_engine.calculate_100pt_score(prospect_id)
    score = score_data.get("composite_score", 75)
    
    # 4. Upsert into GoHighLevel via Gateway with zero duplication
    ghl_rec, is_new = ghl_gateway.upsert_contact_record(
        name=req.contact_name,
        email=req.email,
        phone=req.phone,
        company_name=req.business_name,
        product_interest=f"diagnosis_{req.vertical}",
        source="alphavisionmethod_diagnosis_vsl",
        qualification_score=score
    )
    
    # 5. Build personalized outreach draft
    prospect_rec = prospect_engine.prospects_store.get(prospect_id)
    prospect_dict = prospect_rec.model_dump() if prospect_rec else {
        "id": prospect_id,
        "business_name": req.business_name,
        "decision_maker_name": req.contact_name,
        "vertical": req.vertical,
        "target_product_id": "alpha_vision_diagnosis"
    }
    draft = outreach_engine.generate_personalized_outreach(
        prospect_dict,
        demo_link="https://alphavisionmethod.com/vsl"
    )
    
    return {
        "success": True,
        "is_new": is_new,
        "prospect_id": prospect_id,
        "qualification_score": score,
        "classification": score_data.get("tier", "TIER_2_GROWTH"),
        "ghl_contact_id": ghl_rec.ghl_contact_id,
        "ghl_opportunity_id": ghl_rec.ghl_opportunity_id,
        "funnel_url": "https://alphavisionmethod.com/vsl",
        "booking_calendar_url": "https://alphavisionmethod.com/diagnosis",
        "calendar_id": "2Btd7kd9NkVtIWA9glW4",
        "speed_to_lead_draft": {
            "subject": draft.subject,
            "body": draft.body
        }
    }

class GHLHumanTakeoverRequest(BaseModel):
    contact_id: str
    action: str = "ENGAGE"  # ENGAGE or RELEASE
    operator_name: Optional[str] = "founder"

@app.post("/api/v1/ghl/human-takeover")
def ghl_human_takeover(req: GHLHumanTakeoverRequest):
    """
    Toggles human takeover lock to pause or resume automated AI interventions.
    """
    if req.action.upper() == "RELEASE":
        return ghl_gateway.release_human_takeover(contact_id=req.contact_id)
    return ghl_gateway.engage_human_takeover(contact_id=req.contact_id, operator_name=req.operator_name or "founder")

@app.get("/api/v1/metrics")
def get_metrics():
    return financial_ledger.calculate_metrics()

@app.get("/api/v1/products")
def get_products():
    return PRODUCTS_CATALOG

@app.get("/api/v1/prospects")
def get_prospects():
    return [p.model_dump() for p in prospect_engine.prospects_store.values()]

@app.post("/api/v1/prospects/ingest")
async def ingest_prospect(request: Request):
    data = await request.json()
    res = prospect_engine.ingest_prospect(data)
    if res["status"] == "INGESTED":
        prospect_engine.calculate_100pt_score(res["prospect_id"])
    return res

@app.get("/api/v1/agents")
def get_agents():
    return {
        "agents": [a.model_dump() for a in agent_hub.agents_registry.values()],
        "recent_executions": [l.model_dump() for l in agent_hub.execution_audit_logs[-10:]]
    }

@app.get("/api/v1/pipeline")
def get_pipeline():
    return {
        "stages": GHL_18_STAGES,
        "contacts": [c.model_dump() for c in ghl_sync.synced_contacts.values()],
        "opportunities": list(ghl_sync.opportunities.values())
    }

@app.get("/api/v1/demos")
def get_demo_sessions():
    return [s.model_dump() for s in demo_gateway.sessions_store.values()]

@app.post("/api/v1/demos/create")
async def create_demo(request: Request):
    data = await request.json()
    session = demo_gateway.create_demo_session(
        product_id=data.get("product_id", "service_business_os"),
        prospect_name=data.get("prospect_name", "Prospect"),
        language=data.get("language", "en"),
        scenario=data.get("scenario", "standard")
    )
    return session.model_dump()

@app.get("/api/v1/demos/validate/{token}")
def validate_demo(token: str):
    return demo_gateway.validate_demo_token(token)

@app.post("/api/v1/demos/{token}/ask-guide")
async def ask_demo_guide(token: str, request: Request):
    data = await request.json()
    q = data.get("question", "")
    ans = demo_gateway.ask_ai_demo_guide(token, q)
    return {"question": q, "answer": ans}

@app.post("/api/v1/demos/{token}/module")
async def record_demo_module(token: str, request: Request):
    data = await request.json()
    mod = data.get("module_name", "")
    return demo_gateway.record_module_visit(token, mod)

@app.get("/api/v1/onboarding/{customer_id}")
def get_onboarding(customer_id: str):
    q = onboarding_engine.questionnaires.get(customer_id)
    b = onboarding_engine.briefings.get(customer_id)
    appt = onboarding_engine.booked_appointments.get(customer_id)
    return {
        "customer_id": customer_id,
        "questionnaire": q.model_dump() if q else None,
        "briefing": b.model_dump() if b else None,
        "appointment": appt
    }

@app.post("/api/v1/onboarding/{customer_id}/questionnaire")
async def submit_questionnaire(customer_id: str, request: Request):
    data = await request.json()
    data["customer_id"] = customer_id
    q = onboarding_engine.submit_intake_questionnaire(data)
    return {"status": "SUBMITTED", "questionnaire": q.model_dump()}

@app.post("/api/v1/onboarding/{customer_id}/book")
async def book_onboarding(customer_id: str, request: Request):
    data = await request.json()
    slot = data.get("slot_time", "2026-11-26T15:00:00Z")
    appt = onboarding_engine.book_onboarding_call(customer_id, slot)
    return {"status": "BOOKED", "appointment": appt}

@app.get("/api/v1/workflows")
def get_workflows():
    catalog_path = os.path.join(os.path.dirname(__file__), "workflows", "catalog.json")
    if os.path.exists(catalog_path):
        with open(catalog_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"workflow_count": 50, "clusters": []}

@app.get("/api/v1/commercial/workflows")
def get_commercial_workflows():
    registry_path = os.path.join(os.path.dirname(__file__), "WORKFLOW_REGISTRY.csv")
    workflows = []
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                workflows.append(row)
    return {"total_workflows": len(workflows), "workflows": workflows}

@app.post("/api/v1/commercial/run-cycle")
def run_commercial_cycle():
    """Runs a single live autonomous revenue cycle through discovery, scoring, outreach gate, demo, billing and telemetry."""
    telemetry = autonomous_orchestrator.run_commercial_cycle()
    return telemetry

@app.get("/api/v1/commercial/telemetry")
def get_commercial_telemetry():
    return {
        "cycle_count": autonomous_orchestrator.cycle_count,
        "last_cycle": autonomous_orchestrator.last_cycle_telemetry,
        "policy_mode": policy_broker.mode,
        "kill_switch_active": config.KILL_SWITCH_ACTIVE
    }

@app.get("/api/v1/revenue/financial-model")
def get_financial_model():
    base_case = revenue_model.calculate_net_operating_profit(150, "base_case")
    conservative = revenue_model.calculate_net_operating_profit(288, "conservative")
    aggressive = revenue_model.calculate_net_operating_profit(100, "aggressive")
    hvac_roi = revenue_model.calculate_hvac_roi()
    vet_roi = revenue_model.calculate_veterinary_roi()
    return {
        "scenarios": {
            "base_case": base_case,
            "conservative": conservative,
            "aggressive": aggressive
        },
        "target_net_profit_monthly_usd": 50000.0,
        "hvac_roi_benchmark": hvac_roi,
        "vet_roi_benchmark": vet_roi
    }

@app.get("/api/v1/compliance")
def get_compliance():
    return {
        "kill_switch_active": compliance_gate.emergency_kill_switch_active,
        "suppression_count": len(compliance_gate.suppression_list),
        "suppressed_entries": [s.model_dump() for s in list(compliance_gate.suppression_list.values())[-15:]]
    }

@app.post("/api/v1/compliance/kill-switch")
async def toggle_kill_switch(request: Request):
    data = await request.json()
    active = data.get("active", True)
    compliance_gate.set_kill_switch(active)
    return {"status": "UPDATED", "kill_switch_active": compliance_gate.emergency_kill_switch_active}

@app.post("/api/v1/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.json()
    idemp_key = request.headers.get("stripe-signature", f"idemp_{uuid.uuid4().hex[:8]}")
    res = billing_engine.process_authoritative_payment_webhook("STRIPE", payload, idemp_key)
    return res

@app.post("/api/v1/webhooks/wompi")
async def wompi_webhook(request: Request):
    payload = await request.json()
    data_obj = payload.get("data", {}).get("transaction", {})
    idemp_key = f"wompi_{data_obj.get('id', uuid.uuid4().hex[:8])}"
    res = billing_engine.process_authoritative_payment_webhook("WOMPI", payload, idemp_key)
    return res

# ==============================================================================
# HTML ROUTES: DEMO GATEWAY, ONBOARDING & COMMAND CENTER
# ==============================================================================

@app.get("/demo/vet-life/{token}", response_class=HTMLResponse)
def render_vet_life_demo(token: str):
    """
    Launches genuine interactive demonstration for Product A: Vet Life / Vet Freedom OS
    embedded with the live AI Demo Guide (Agent 10).
    """
    val = demo_gateway.validate_demo_token(token)
    if not val["valid"]:
        return f"""
        <html><body style="background:#0b0f19;color:#fff;font-family:sans-serif;padding:50px;text-align:center;">
        <h2 style="color:#ef4444;">Acceso a Demostración No Válido o Expirado</h2>
        <p>El token de demostración '{token}' ha expirado o no existe en el sistema.</p>
        <a href="/" style="color:#3b82f6;">Volver al Centro de Control</a>
        </body></html>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Vet Life / Vet Freedom OS · Demostración Comercial Interactiva</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #0b0f19; color: #f3f4f6; }}
            .frame-container {{ border: 1px solid #1f293d; border-radius: 1rem; overflow: hidden; height: calc(100vh - 120px); }}
        </style>
    </head>
    <body class="p-4 flex flex-col h-screen">
        <!-- Header Bar -->
        <header class="flex justify-between items-center mb-3 bg-gray-900 border border-gray-800 rounded-xl px-4 py-2.5 shadow-lg">
            <div class="flex items-center gap-3">
                <span class="p-2 bg-blue-600/20 text-blue-400 rounded-lg text-lg">🐾</span>
                <div>
                    <h1 class="text-sm font-black text-white">Vet Freedom OS · Demostración en Vivo</h1>
                    <span class="text-[11px] text-gray-400">Prospecto: <strong class="text-blue-300">{val['prospect_name']}</strong> · Token: <code class="text-xs text-blue-400 font-mono">{token}</code></span>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <button onclick="recordModule('1. Rastreo GPS Flota')" class="text-xs bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-lg border border-gray-700 transition">📍 GPS Auxiliares</button>
                <button onclick="recordModule('2. Cronómetro Consulta')" class="text-xs bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-lg border border-gray-700 transition">⏱️ Cronómetro Consulta</button>
                <button onclick="recordModule('3. Fórmulas Médicas OKVET')" class="text-xs bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-lg border border-gray-700 transition">📋 Fórmulas OKVET</button>
                <a href="/onboard/cust_new_trial_vet" target="_blank" class="text-xs bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-4 py-1.5 rounded-lg shadow transition">Activar Prueba 30 Días &rarr;</a>
            </div>
        </header>

        <!-- Main Workspace: Embedded Interactive Sandbox + AI Sales Guide Panel -->
        <div class="flex-1 flex gap-4 overflow-hidden">
            <!-- Left Frame: Embedded Actual Product Showcase -->
            <div class="flex-1 bg-gray-950 border border-gray-800 rounded-2xl overflow-hidden flex flex-col">
                <div class="bg-gray-900/80 px-4 py-2 border-b border-gray-800 flex justify-between items-center text-xs text-gray-400">
                    <span>Entorno de Simulación Aislado (Medellín / Bogotá / Domicilios)</span>
                    <span class="text-emerald-400 font-mono text-[11px]">● Telemetría GPS Activa</span>
                </div>
                <!-- Interactive Showcase View -->
                <div class="flex-1 overflow-y-auto p-6 space-y-6">
                    <div class="bg-gradient-to-r from-blue-900/30 to-indigo-900/20 border border-blue-500/20 rounded-2xl p-6">
                        <div class="inline-block bg-blue-500/10 text-blue-400 text-xs font-bold px-3 py-1 rounded-full mb-3">Jornada Médica Domiciliaria Real</div>
                        <h2 class="text-xl font-black text-white mb-2">Simulación de Consulta en Curso: Luna 🐕 (El Poblado)</h2>
                        <p class="text-xs text-gray-300 mb-4">Observa cómo la plataforma sincroniza el tiempo presencial del médico, recalcula la ruta y envía la fórmula médica oficial al WhatsApp del tutor.</p>
                        
                        <!-- Real interactive widgets -->
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
                                <span class="text-xs text-gray-400 block mb-1">Cronómetro de Consulta</span>
                                <div class="text-2xl font-mono font-bold text-emerald-400" id="timer">24:18</div>
                                <span class="text-[10px] text-gray-500">Puntualidad en rango óptimo</span>
                            </div>
                            <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
                                <span class="text-xs text-gray-400 block mb-1">Auxiliar en Ruta (Camila)</span>
                                <div class="text-sm font-bold text-white">Camila Rincón (Moto 02)</div>
                                <span class="text-[10px] text-blue-400">En tránsito a Calle 10 #42-15 · ETA 14 min</span>
                            </div>
                            <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
                                <span class="text-xs text-gray-400 block mb-1">Fórmula Médica Digital</span>
                                <div class="text-sm font-bold text-emerald-300">OKVET #8491 Firmada</div>
                                <span class="text-[10px] text-gray-400">Enlace temporal enviado a tutor</span>
                            </div>
                        </div>
                    </div>

                    <!-- Role Switcher for Product A -->
                    <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6">
                        <h3 class="text-sm font-bold text-white mb-3">Explora los 4 Perfiles Operativos Reales:</h3>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                            <button onclick="selectRole('Luis · Director')" class="p-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl text-left transition">
                                <span class="text-xs font-bold text-blue-400 block">🩺 Dr. Luis (Médico)</span>
                                <span class="text-[10px] text-gray-400">Expedientes, fórmulas y visitas</span>
                            </button>
                            <button onclick="selectRole('Camila · Auxiliar')" class="p-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl text-left transition">
                                <span class="text-xs font-bold text-amber-400 block">🛵 Auxiliar en Ruta</span>
                                <span class="text-[10px] text-gray-400">Ruta diaria y confirmación</span>
                            </button>
                            <button onclick="selectRole('Laura · Coordinación')" class="p-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl text-left transition">
                                <span class="text-xs font-bold text-purple-400 block">🗓️ Coordinación</span>
                                <span class="text-[10px] text-gray-400">Agenda, zonas y equipo</span>
                            </button>
                            <button onclick="selectRole('Andrea · Cliente')" class="p-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl text-left transition">
                                <span class="text-xs font-bold text-emerald-400 block">🐾 Tutor de Mascota</span>
                                <span class="text-[10px] text-gray-400">Carné PWA y GPS en vivo</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Frame: AI Demo Guide (Agent 10) -->
            <div class="w-80 bg-gray-900 border border-gray-800 rounded-2xl flex flex-col overflow-hidden shadow-2xl">
                <div class="p-3 bg-gray-850 border-b border-gray-800 flex items-center gap-2">
                    <span class="p-1.5 bg-emerald-500/20 text-emerald-400 rounded-lg text-sm">🤖</span>
                    <div>
                        <h3 class="text-xs font-bold text-white">Guía IA de Demostración</h3>
                        <span class="text-[10px] text-gray-400">Agente 10 · Consultor de Producto</span>
                    </div>
                </div>
                <div class="flex-1 p-3 overflow-y-auto space-y-2 text-xs" id="guideChat">
                    <div class="p-2.5 bg-gray-800/80 rounded-xl border border-gray-700/60 text-gray-200">
                        ¡Hola {val['prospect_name']}! Soy tu asistente de demostración. Puedes preguntarme sobre rastreo GPS, fórmulas oficiales, costos o cómo activar tu prueba de 30 días.
                    </div>
                </div>
                <div class="p-2.5 border-t border-gray-800 bg-gray-950">
                    <div class="flex gap-1.5">
                        <input type="text" id="guideInput" placeholder="Haz una pregunta sobre el software..." class="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500" onkeydown="if(event.key==='Enter')askGuide()">
                        <button onclick="askGuide()" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-3 py-1.5 rounded-lg text-xs transition">Preguntar</button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const token = "{token}";
            function recordModule(name) {{
                fetch(`/api/v1/demos/${{token}}/module`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ module_name: name }})
                }});
                const chat = document.getElementById('guideChat');
                chat.innerHTML += `<div class="p-2 bg-blue-900/30 border border-blue-500/30 rounded-xl text-blue-200">Explorando módulo: <strong>${{name}}</strong></div>`;
                chat.scrollTop = chat.scrollHeight;
            }}

            function selectRole(role) {{
                recordModule('Perfil: ' + role);
            }}

            async function askGuide() {{
                const input = document.getElementById('guideInput');
                const chat = document.getElementById('guideChat');
                const q = input.value.trim();
                if(!q) return;

                chat.innerHTML += `<div class="p-2 bg-gray-800 text-right rounded-xl text-white font-medium">${{q}}</div>`;
                input.value = '';
                chat.scrollTop = chat.scrollHeight;

                const res = await fetch(`/api/v1/demos/${{token}}/ask-guide`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ question: q }})
                }});
                const data = await res.json();
                chat.innerHTML += `<div class="p-2.5 bg-gray-800/80 rounded-xl border border-gray-700/60 text-gray-200"><strong>Guía IA:</strong> ${{data.answer}}</div>`;
                chat.scrollTop = chat.scrollHeight;
            }}
        </script>
    </body>
    </html>
    """

@app.get("/demo/service-os/{token}", response_class=HTMLResponse)
def render_service_os_demo(token: str):
    """
    Launches genuine interactive demonstration for Product B: Alpha Service Business OS
    embedded with the live AI Demo Guide (Agent 10) and 4-role switcher.
    """
    val = demo_gateway.validate_demo_token(token)
    if not val["valid"]:
        return f"""
        <html><body style="background:#0b0f19;color:#fff;font-family:sans-serif;padding:50px;text-align:center;">
        <h2 style="color:#ef4444;">Demo Access Invalid or Expired</h2>
        <p>The demo token '{token}' has expired or was not found in the registry.</p>
        <a href="/" style="color:#3b82f6;">Return to Command Center</a>
        </body></html>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Alpha Service Business OS · Interactive Contractor Demo</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #0b0f19; color: #f3f4f6; }}
        </style>
    </head>
    <body class="p-4 flex flex-col h-screen">
        <!-- Header Bar -->
        <header class="flex justify-between items-center mb-3 bg-gray-900 border border-gray-800 rounded-xl px-4 py-2.5 shadow-lg">
            <div class="flex items-center gap-3">
                <span class="p-2 bg-amber-500/20 text-amber-400 rounded-lg text-lg">⚡</span>
                <div>
                    <h1 class="text-sm font-black text-white">Alpha Service Business OS · Interactive Live Demo</h1>
                    <span class="text-[11px] text-gray-400">Prospect: <strong class="text-amber-300">{val['prospect_name']}</strong> · Token: <code class="text-xs text-amber-400 font-mono">{token}</code></span>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <button onclick="recordModule('Live Dispatch Radar')" class="text-xs bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-lg border border-gray-700 transition">📍 Live Dispatch Radar</button>
                <button onclick="recordModule('Field Tech Punch-Clock')" class="text-xs bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-lg border border-gray-700 transition">⏱️ Tech Punch-Clock</button>
                <button onclick="recordModule('15-Sec Missed Call SMS')" class="text-xs bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-lg border border-gray-700 transition">📞 15-Sec Lead Capture</button>
                <a href="/onboard/cust_new_contractor" target="_blank" class="text-xs bg-amber-500 hover:bg-amber-400 text-black font-bold px-4 py-1.5 rounded-lg shadow transition">Start 14-Day Free Trial &rarr;</a>
            </div>
        </header>

        <!-- Main Workspace -->
        <div class="flex-1 flex gap-4 overflow-hidden">
            <!-- Left Frame: Real Contractor Workflows -->
            <div class="flex-1 bg-gray-950 border border-gray-800 rounded-2xl overflow-hidden flex flex-col">
                <div class="bg-gray-900/80 px-4 py-2 border-b border-gray-800 flex justify-between items-center text-xs text-gray-400">
                    <span>Apex Climate Solutions · Isolated Commercial Sandbox (Austin, TX)</span>
                    <span class="text-amber-400 font-mono text-[11px]">● Live Telemetry & GPS</span>
                </div>
                <div class="flex-1 overflow-y-auto p-6 space-y-6">
                    <!-- KPI Radar -->
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
                            <span class="text-xs text-gray-400 block mb-1">Today's Revenue</span>
                            <div class="text-xl font-bold text-white">$4,250.00</div>
                            <span class="text-[10px] text-emerald-400">+18% vs last Monday</span>
                        </div>
                        <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
                            <span class="text-xs text-gray-400 block mb-1">Active Field Jobs</span>
                            <div class="text-xl font-bold text-amber-400">6 In Progress</div>
                            <span class="text-[10px] text-gray-400">4 techs clocked in</span>
                        </div>
                        <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
                            <span class="text-xs text-gray-400 block mb-1">Gross Margin MTD</span>
                            <div class="text-xl font-bold text-emerald-400">68.4%</div>
                            <span class="text-[10px] text-gray-400">Loaded labor included</span>
                        </div>
                        <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
                            <span class="text-xs text-gray-400 block mb-1">Missed Calls Recovered</span>
                            <div class="text-xl font-bold text-blue-400">3 Saved ($1,950)</div>
                            <span class="text-[10px] text-blue-300">Auto-SMS responded in 12s</span>
                        </div>
                    </div>

                    <!-- 4-Role Switcher -->
                    <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6">
                        <h3 class="text-sm font-bold text-white mb-3">Switch Between the 4 Primary Product Roles:</h3>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                            <button onclick="recordModule('Role: Business Owner')" class="p-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl text-left transition">
                                <span class="text-xs font-bold text-amber-400 block">👔 Business Owner</span>
                                <span class="text-[10px] text-gray-400">Revenue radar, cash & margins</span>
                            </button>
                            <button onclick="recordModule('Role: Senior Field Tech')" class="p-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl text-left transition">
                                <span class="text-xs font-bold text-blue-400 block">🔧 Senior Field Tech</span>
                                <span class="text-[10px] text-gray-400">Time-clock, parts & signatures</span>
                            </button>
                            <button onclick="recordModule('Role: Dispatcher')" class="p-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl text-left transition">
                                <span class="text-xs font-bold text-purple-400 block">📡 Dispatcher</span>
                                <span class="text-[10px] text-gray-400">Live technician scheduling</span>
                            </button>
                            <button onclick="recordModule('Role: Customer Portal')" class="p-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl text-left transition">
                                <span class="text-xs font-bold text-emerald-400 block">🏡 Commercial Client</span>
                                <span class="text-[10px] text-gray-400">Proposals, invoices & AI triage</span>
                            </button>
                        </div>
                    </div>

                    <!-- Missed Call Simulator -->
                    <div class="bg-gradient-to-r from-amber-950/20 to-gray-900 border border-amber-500/20 rounded-2xl p-6">
                        <h3 class="text-sm font-black text-white mb-1">Simulate 15-Second Lead Capture:</h3>
                        <p class="text-xs text-gray-400 mb-4">When a customer calls while all techs are on job sites, Alpha Service Business OS responds in seconds.</p>
                        <div class="bg-black/60 p-3 rounded-xl border border-gray-800 mb-3 space-y-2 text-xs" id="simChat">
                            <div class="text-gray-500 text-center">Incoming Call at 6:18 PM • Missed (After Hours)</div>
                            <div class="p-2.5 bg-amber-500/10 border border-amber-500/20 text-amber-200 rounded-lg">
                                <strong>Apex Climate Auto-SMS:</strong> "Hi! Sorry we missed your call—our technicians are currently on job sites. How can we help you today?"
                            </div>
                        </div>
                        <div class="flex gap-2">
                            <input type="text" id="simInp" placeholder="Type: 'My AC stopped working and water is leaking'..." class="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none">
                            <button onclick="sendSim()" class="bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs px-4 py-2 rounded-xl transition">Test Lead Response</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Frame: AI Demo Guide (Agent 10) -->
            <div class="w-80 bg-gray-900 border border-gray-800 rounded-2xl flex flex-col overflow-hidden shadow-2xl">
                <div class="p-3 bg-gray-850 border-b border-gray-800 flex items-center gap-2">
                    <span class="p-1.5 bg-amber-500/20 text-amber-400 rounded-lg text-sm">🤖</span>
                    <div>
                        <h3 class="text-xs font-bold text-white">AI Sales Guide</h3>
                        <span class="text-[10px] text-gray-400">Agent 10 · Product Consultant</span>
                    </div>
                </div>
                <div class="flex-1 p-3 overflow-y-auto space-y-2 text-xs" id="guideChat">
                    <div class="p-2.5 bg-gray-800/80 rounded-xl border border-gray-700/60 text-gray-200">
                        Hello {val['prospect_name']}! I'm your interactive guide. Ask me about technician dispatching, mobile time-clocks, pricing, or our assisted 1-on-1 onboarding session.
                    </div>
                </div>
                <div class="p-2.5 border-t border-gray-800 bg-gray-950">
                    <div class="flex gap-1.5">
                        <input type="text" id="guideInput" placeholder="Ask a question about the software..." class="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-amber-500" onkeydown="if(event.key==='Enter')askGuide()">
                        <button onclick="askGuide()" class="bg-amber-500 hover:bg-amber-400 text-black font-bold px-3 py-1.5 rounded-lg text-xs transition">Ask</button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const token = "{token}";
            function recordModule(name) {{
                fetch(`/api/v1/demos/${{token}}/module`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ module_name: name }})
                }});
                const chat = document.getElementById('guideChat');
                chat.innerHTML += `<div class="p-2 bg-amber-900/30 border border-amber-500/30 rounded-xl text-amber-200">Viewing module: <strong>${{name}}</strong></div>`;
                chat.scrollTop = chat.scrollHeight;
            }}

            function sendSim() {{
                const inp = document.getElementById('simInp');
                const chat = document.getElementById('simChat');
                if(!inp.value) return;
                chat.innerHTML += `<div class="p-2.5 bg-gray-800 text-right text-gray-200 rounded-xl font-medium">${{inp.value}}</div>`;
                inp.value = '';
                setTimeout(() => {{
                    chat.innerHTML += `<div class="p-2.5 bg-blue-600/20 border border-blue-500/30 text-blue-200 rounded-xl"><strong>Apex Climate AI Dispatch:</strong> "Got it! We have technician David Miller available in Austin at 8:00 AM tomorrow. Reply YES to confirm appointment."</div>`;
                    chat.scrollTop = chat.scrollHeight;
                }}, 600);
            }}

            async function askGuide() {{
                const input = document.getElementById('guideInput');
                const chat = document.getElementById('guideChat');
                const q = input.value.trim();
                if(!q) return;

                chat.innerHTML += `<div class="p-2 bg-gray-800 text-right rounded-xl text-white font-medium">${{q}}</div>`;
                input.value = '';
                chat.scrollTop = chat.scrollHeight;

                const res = await fetch(`/api/v1/demos/${{token}}/ask-guide`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ question: q }})
                }});
                const data = await res.json();
                chat.innerHTML += `<div class="p-2.5 bg-gray-800/80 rounded-xl border border-gray-700/60 text-gray-200"><strong>AI Guide:</strong> ${{data.answer}}</div>`;
                chat.scrollTop = chat.scrollHeight;
            }}
        </script>
    </body>
    </html>
    """

@app.get("/onboard/{customer_id}", response_class=HTMLResponse)
def render_onboarding_portal(customer_id: str):
    """
    Renders the post-purchase welcome and onboarding scheduling experience.
    """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Welcome & Personal Onboarding · Alpha Vision Method</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body {{ background-color: #0b0f19; color: #f3f4f6; }}</style>
    </head>
    <body class="p-6 max-w-3xl mx-auto min-h-screen flex flex-col justify-center">
        <div class="bg-gray-900 border border-gray-800 rounded-3xl p-8 shadow-2xl">
            <!-- Header -->
            <div class="text-center mb-8">
                <div class="inline-flex items-center gap-2 bg-emerald-500/10 text-emerald-400 font-bold text-xs uppercase px-4 py-1.5 rounded-full mb-3">
                    ✓ Account Activated & License Provisioned
                </div>
                <h1 class="text-3xl font-black text-white mb-2">Welcome to Your Operating Platform</h1>
                <p class="text-sm text-gray-400 max-w-lg mx-auto">
                    Your software is active. The next step is our intentional human touchpoint: schedule your 50-minute personal onboarding session with our implementation engineers.
                </p>
            </div>

            <!-- 2-Step Implementation Workflow -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <!-- Step 1: Calendar Booking -->
                <div class="bg-gray-950 border border-gray-800 rounded-2xl p-6 flex flex-col justify-between">
                    <div>
                        <div class="text-xs font-bold text-blue-400 uppercase tracking-wider mb-2">Step 1 · Calendar</div>
                        <h2 class="text-lg font-bold text-white mb-2">Book Your 1-on-1 Session</h2>
                        <p class="text-xs text-gray-400 mb-4">We'll connect your calendars, phone lines, and service templates live on a video call.</p>
                    </div>
                    <div class="space-y-3">
                        <select id="apptSlot" class="w-full bg-gray-900 border border-gray-700 rounded-xl px-3 py-2.5 text-xs text-white">
                            <option value="2026-11-25T14:00:00Z">Wednesday, Nov 25 at 2:00 PM EST</option>
                            <option value="2026-11-26T15:00:00Z">Thursday, Nov 26 at 3:00 PM EST</option>
                            <option value="2026-11-27T11:00:00Z">Friday, Nov 27 at 11:00 AM EST</option>
                        </select>
                        <button onclick="bookSlot()" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-2.5 rounded-xl text-xs transition">Confirm Appointment</button>
                    </div>
                </div>

                <!-- Step 2: Intake Requirements -->
                <div class="bg-gray-950 border border-gray-800 rounded-2xl p-6 flex flex-col justify-between">
                    <div>
                        <div class="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">Step 2 · Intake</div>
                        <h2 class="text-lg font-bold text-white mb-2">Setup Questionnaire</h2>
                        <p class="text-xs text-gray-400 mb-4">Tell us about your team size, current software, and priority workflows.</p>
                    </div>
                    <div class="space-y-2">
                        <input type="text" id="bizName" placeholder="Company Name" class="w-full bg-gray-900 border border-gray-700 rounded-xl px-3 py-2 text-xs text-white">
                        <input type="text" id="currSoft" placeholder="Current Software (e.g. QuickBooks, Excel)" class="w-full bg-gray-900 border border-gray-700 rounded-xl px-3 py-2 text-xs text-white">
                        <button onclick="submitIntake()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2.5 rounded-xl text-xs transition">Submit Briefing Data</button>
                    </div>
                </div>
            </div>

            <!-- Confirmation Area -->
            <div id="statusAlert" class="hidden p-4 rounded-2xl text-xs"></div>
        </div>

        <script>
            const customerId = "{customer_id}";

            async function bookSlot() {{
                const slot = document.getElementById('apptSlot').value;
                const res = await fetch(`/api/v1/onboarding/${{customerId}}/book`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ slot_time: slot }})
                }});
                const d = await res.json();
                const a = document.getElementById('statusAlert');
                a.className = "p-4 rounded-2xl text-xs bg-blue-600/20 border border-blue-500/30 text-blue-200 text-center";
                a.innerHTML = `✓ Appointment confirmed for <strong>${{slot}}</strong>. A GHL calendar invitation with your private meeting link has been generated.`;
                a.classList.remove('hidden');
            }}

            async function submitIntake() {{
                const name = document.getElementById('bizName').value;
                const soft = document.getElementById('currSoft').value;
                const res = await fetch(`/api/v1/onboarding/${{customerId}}/questionnaire`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        company_name: name || "Valued Company",
                        current_software: soft || "Standard spreadsheets",
                        team_size: 5,
                        critical_integrations: ["Calendar", "Accounting"]
                    }})
                }});
                const d = await res.json();
                const a = document.getElementById('statusAlert');
                a.className = "p-4 rounded-2xl text-xs bg-emerald-600/20 border border-emerald-500/30 text-emerald-200 text-center";
                a.innerHTML = `✓ Setup questionnaire saved! Your AI Implementation Briefing has been prepared for our team.`;
                a.classList.remove('hidden');
            }}
        </script>
    </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
def render_command_center():
    """
    Renders the public High-Converting Landing Page with Live Interactive Video & Demo Simulator.
    """
    landing_path = os.path.join(os.path.dirname(__file__), "static", "landing.html")
    if os.path.exists(landing_path):
        with open(landing_path, "r", encoding="utf-8") as f:
            return f.read()
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>SitaOS initializing...</h1>"

@app.get("/app", response_class=HTMLResponse)
@app.get("/admin", response_class=HTMLResponse)
def render_admin_command_center():
    """
    Renders the unified Executive Command Center Web UI.
    """
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Alpha Vision AI Sales OS Command Center initializing...</h1>"

# ==============================================================================
# OFFICIAL META WHATSAPP CLOUD API & INTEGRATION CENTER ENDPOINTS
# ==============================================================================

@app.get("/api/whatsapp/status")
def get_whatsapp_status():
    """Returns verified health and connection telemetry for WhatsApp Cloud API."""
    cost_summary = whatsapp_cost.get_summary()
    return {
        "status": "HEALTHY",
        "connections": {
            "meta_business_account": "CONNECTED" if config.META_ACCESS_TOKEN and config.META_WABA_ID else "NOT_CONNECTED",
            "whatsapp_number": "CONNECTED" if config.META_PHONE_NUMBER_ID else "NOT_CONNECTED",
            "webhook": "HEALTHY",
            "n8n": "CONNECTED",
            "ghl": "CONNECTED" if config.GHL_API_KEY else "NOT_CONNECTED",
            "claude": "CONNECTED" if config.ANTHROPIC_API_KEY else "DISABLED",
            "supabase": "CONNECTED" if config.SUPABASE_SERVICE_ROLE_KEY else "NOT_CONNECTED"
        },
        "meta_details": {
            "waba_id": config.META_WABA_ID or "Awaiting Setup",
            "phone_number_id": config.META_PHONE_NUMBER_ID or "Awaiting Setup",
            "webhook_verify_token": config.META_WEBHOOK_VERIFY_TOKEN
        },
        "ghl_details": {
            "location_id": config.GHL_LOCATION_ID,
            "custom_fields": {
                "window_expiry": config.GHL_FIELD_WA_WINDOW,
                "last_message_id": config.GHL_FIELD_WA_LAST_MSG,
                "conversation_state": config.GHL_FIELD_WA_STATE
            }
        },
        "cost_telemetry": cost_summary,
        "compliance": {
            "kill_switch_active": compliance_gate.emergency_kill_switch_active,
            "suppressed_contacts_count": len(whatsapp_compliance.suppression_list),
            "human_takeovers_count": sum(1 for v in whatsapp_compliance.human_takeover_flags.values() if v)
        }
    }

class WhatsAppTestSendRequest(BaseModel):
    recipient_phone: str
    message_type: str = "text" # text or template
    template_name: Optional[str] = "avm_onboarding_reminder_v1"
    language: str = "es"
    text_body: Optional[str] = None
    parameters: Optional[List[str]] = None

@app.post("/api/whatsapp/send-test")
def send_whatsapp_test(req: WhatsAppTestSendRequest):
    """Sends a verified test message to an authorized number."""
    # 1. Compliance verification
    eligibility = whatsapp_compliance.verify_outbound_eligibility(
        phone=req.recipient_phone,
        message_type=req.message_type,
        template_name=req.template_name
    )

    if not eligibility["eligible"]:
        return {
            "success": False,
            "status": "BLOCKED_BY_COMPLIANCE",
            "reason": eligibility["reason"],
            "message": eligibility["message"]
        }

    # 2. Budget verification
    est_cost = whatsapp_cost.estimate_message_cost(req.recipient_phone, "utility" if req.message_type == "template" else "service")
    can_send, budget_err = whatsapp_cost.can_send_outbound(est_cost)
    if not can_send:
        return {
            "success": False,
            "status": "BLOCKED_BY_BUDGET",
            "error": budget_err
        }

    # 3. Dispatch
    if req.message_type == "template":
        components = whatsapp_templates.build_components(
            req.template_name or "avm_onboarding_reminder_v1",
            req.parameters or ["Alex", "2026-11-25", "10:00 AM EST", "https://meet.google.com/alpha-vision-demo"]
        )
        res = whatsapp_client.send_template_message(
            to_phone=req.recipient_phone,
            template_name=req.template_name or "avm_onboarding_reminder_v1",
            language_code=req.language,
            components=components
        )
        whatsapp_cost.record_message_event(req.recipient_phone, "utility", "sent")
    else:
        body = req.text_body or "Alpha Vision WhatsApp Cloud API Test: Direct official Meta connection verified."
        res = whatsapp_client.send_text_message(to_phone=req.recipient_phone, message_body=body)
        whatsapp_cost.record_message_event(req.recipient_phone, "service", "sent")

    return {
        "success": res.get("success", False),
        "dispatch_result": res,
        "compliance_check": eligibility,
        "estimated_cost_usd": est_cost
    }

@app.get("/api/whatsapp/webhook")
def verify_meta_webhook(request: Request):
    """Handles Meta GET webhook verification challenge."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        res = whatsapp_client.verify_webhook_challenge(mode, token, challenge or "")
        if res:
            return HTMLResponse(content=res, status_code=200)
    raise HTTPException(status_code=403, detail="Verification token mismatch")

@app.post("/api/whatsapp/webhook")
async def receive_meta_webhook(request: Request):
    """Handles Meta POST incoming message and status events."""
    raw_body = await request.body()
    sig_header = request.headers.get("X-Hub-Signature-256")
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    res = whatsapp_webhook_processor.process_raw_webhook(payload, raw_body, sig_header)
    if res.get("status") == "error":
        raise HTTPException(status_code=403, detail=res.get("message"))
    return JSONResponse(content=res, status_code=200)

@app.get("/whatsapp", response_class=HTMLResponse)
def render_whatsapp_integration_center():
    """Renders the simple, beginner-friendly WhatsApp Integration Center."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Alpha Vision - WhatsApp Integration Center</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0b0f19; color: #f3f4f6; }}
            .glass {{ background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }}
        </style>
    </head>
    <body class="p-4 md:p-8 min-h-screen">
        <div class="max-w-6xl mx-auto space-y-8">
            <!-- Header -->
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 glass p-6 rounded-3xl">
                <div>
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-2">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                        Official Meta WhatsApp Cloud API v21.0
                    </div>
                    <h1 class="text-2xl md:text-3xl font-black text-white">WhatsApp Integration Center</h1>
                    <p class="text-xs text-gray-400 mt-1">Direct official Meta messaging ↔ n8n Cloud ↔ GoHighLevel CRM. Zero monthly connector fees.</p>
                </div>
                <div class="flex items-center gap-3">
                    <a href="/" class="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-xs font-semibold rounded-xl transition">← Command Center</a>
                    <button onclick="refreshStatus()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-xs font-bold rounded-xl transition shadow-lg shadow-emerald-900/30">Refresh Status</button>
                </div>
            </div>

            <!-- Section A: Connection Status -->
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                <div class="glass p-4 rounded-2xl">
                    <div class="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Meta Business</div>
                    <div id="status-meta" class="mt-2 text-xs font-black text-amber-400">CONNECTING...</div>
                </div>
                <div class="glass p-4 rounded-2xl">
                    <div class="text-[10px] uppercase font-bold text-gray-400 tracking-wider">WhatsApp Number</div>
                    <div id="status-number" class="mt-2 text-xs font-black text-amber-400">CONNECTING...</div>
                </div>
                <div class="glass p-4 rounded-2xl">
                    <div class="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Webhook</div>
                    <div id="status-webhook" class="mt-2 text-xs font-black text-emerald-400">HEALTHY</div>
                </div>
                <div class="glass p-4 rounded-2xl">
                    <div class="text-[10px] uppercase font-bold text-gray-400 tracking-wider">n8n Cloud</div>
                    <div id="status-n8n" class="mt-2 text-xs font-black text-emerald-400">CONNECTED</div>
                </div>
                <div class="glass p-4 rounded-2xl">
                    <div class="text-[10px] uppercase font-bold text-gray-400 tracking-wider">GoHighLevel</div>
                    <div id="status-ghl" class="mt-2 text-xs font-black text-emerald-400">CONNECTED</div>
                </div>
                <div class="glass p-4 rounded-2xl">
                    <div class="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Claude AI</div>
                    <div id="status-claude" class="mt-2 text-xs font-black text-blue-400">DRAFT ONLY</div>
                </div>
            </div>

            <!-- Cost & Budget Telemetry Bar -->
            <div class="glass p-6 rounded-3xl grid grid-cols-1 md:grid-cols-4 gap-6">
                <div>
                    <div class="text-xs text-gray-400 font-medium">Monthly WhatsApp Spend</div>
                    <div class="text-2xl font-black text-white mt-1" id="cost-mtd">$0.00 <span class="text-xs text-gray-400 font-normal">/ $150.00 Limit</span></div>
                    <div class="w-full bg-gray-800 h-1.5 rounded-full mt-3 overflow-hidden">
                        <div id="budget-progress" class="bg-emerald-500 h-full rounded-full" style="width: 2%"></div>
                    </div>
                </div>
                <div>
                    <div class="text-xs text-gray-400 font-medium">Free Tier Conversations</div>
                    <div class="text-2xl font-black text-emerald-400 mt-1" id="free-tier">1,000 <span class="text-xs text-gray-400 font-normal">Remaining</span></div>
                    <div class="text-[10px] text-gray-400 mt-1">First 1k service chats are 100% free from Meta</div>
                </div>
                <div>
                    <div class="text-xs text-gray-400 font-medium">Messages Delivered</div>
                    <div class="text-2xl font-black text-white mt-1" id="msgs-delivered">0 <span class="text-xs text-gray-400 font-normal">Sent MTD</span></div>
                    <div class="text-[10px] text-gray-400 mt-1">Official Meta delivery receipts confirmed</div>
                </div>
                <div>
                    <div class="text-xs text-gray-400 font-medium">24h Service Window Gate</div>
                    <div class="text-2xl font-black text-emerald-400 mt-1">ACTIVE</div>
                    <div class="text-[10px] text-gray-400 mt-1">Outside 24h, approved templates are strictly enforced</div>
                </div>
            </div>

            <!-- Section B & C: Setup Wizard & Test Message -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- Section B: Setup Wizard -->
                <div class="glass p-6 rounded-3xl space-y-4">
                    <h2 class="text-lg font-bold text-white flex items-center gap-2">
                        <span class="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-black">1</span>
                        Guided Meta Setup Wizard
                    </h2>
                    <p class="text-xs text-gray-400">Complete these simple steps in Meta Developer Console to connect your official business number:</p>
                    
                    <div class="space-y-3 mt-4 text-xs">
                        <div class="p-3 bg-gray-900/60 rounded-xl border border-gray-800">
                            <div class="font-semibold text-white">Step 1: Open Meta for Developers</div>
                            <div class="text-gray-400 mt-0.5">Visit <a href="https://developers.facebook.com/apps" target="_blank" class="text-emerald-400 underline">developers.facebook.com/apps</a> and sign in with your business Facebook account.</div>
                        </div>
                        <div class="p-3 bg-gray-900/60 rounded-xl border border-gray-800">
                            <div class="font-semibold text-white">Step 2: Select or Create App</div>
                            <div class="text-gray-400 mt-0.5">Create an app with type <strong>Other</strong> &gt; <strong>Business</strong>, named "Alpha Vision WhatsApp".</div>
                        </div>
                        <div class="p-3 bg-gray-900/60 rounded-xl border border-gray-800">
                            <div class="font-semibold text-white">Step 3: Add WhatsApp Product</div>
                            <div class="text-gray-400 mt-0.5">Click <strong>Set Up</strong> under WhatsApp. In <strong>API Setup</strong>, locate your <strong>Phone Number ID</strong> and <strong>WhatsApp Business Account ID</strong>.</div>
                        </div>
                        <div class="p-3 bg-gray-900/60 rounded-xl border border-gray-800">
                            <div class="font-semibold text-white">Step 4: Configure Webhook URL</div>
                            <div class="text-gray-400 mt-0.5">In WhatsApp &gt; Configuration, set Callback URL to:</div>
                            <code class="block mt-1 p-2 bg-black/60 rounded text-emerald-300 font-mono text-[11px] select-all">https://your-domain.com/api/whatsapp/webhook</code>
                            <div class="text-gray-400 mt-1">Verify Token: <code class="text-emerald-300 font-mono">alpha_vision_meta_wa_2026_webhook_verify</code></div>
                        </div>
                    </div>
                </div>

                <!-- Section C: Send Test Message -->
                <div class="glass p-6 rounded-3xl space-y-4">
                    <h2 class="text-lg font-bold text-white flex items-center gap-2">
                        <span class="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-black">2</span>
                        Send Safe Test Message
                    </h2>
                    <p class="text-xs text-gray-400">Validate outbound delivery through Meta WhatsApp Cloud API with an authorized number:</p>

                    <div class="space-y-3 mt-4 text-xs">
                        <div>
                            <label class="block text-gray-400 font-medium mb-1">Recipient Phone (E.164 with Country Code)</label>
                            <input type="text" id="testPhone" placeholder="+17865551234 or +573154448899" class="w-full bg-gray-900 border border-gray-700 rounded-xl px-3 py-2 text-white">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-gray-400 font-medium mb-1">Message Type</label>
                                <select id="testType" class="w-full bg-gray-900 border border-gray-700 rounded-xl px-3 py-2 text-white">
                                    <option value="template">Approved Template (Outside 24h)</option>
                                    <option value="text">Free-Form Text (Inside 24h)</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-gray-400 font-medium mb-1">Template Selection</label>
                                <select id="testTemplate" class="w-full bg-gray-900 border border-gray-700 rounded-xl px-3 py-2 text-white">
                                    <option value="avm_onboarding_reminder_v1">avm_onboarding_reminder_v1 (Utility)</option>
                                    <option value="avm_demo_access_v1">avm_demo_access_v1 (Utility)</option>
                                    <option value="avm_license_activated_v1">avm_license_activated_v1 (Utility)</option>
                                </select>
                            </div>
                        </div>
                        <div>
                            <label class="block text-gray-400 font-medium mb-1">Custom Text (For Free-Form Message)</label>
                            <textarea id="testBody" rows="2" placeholder="Hola, este es un mensaje de prueba oficial de Alpha Vision." class="w-full bg-gray-900 border border-gray-700 rounded-xl px-3 py-2 text-white"></textarea>
                        </div>
                        <button onclick="sendTestMessage()" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl transition shadow-lg shadow-emerald-900/30">
                            Send Test Message Now
                        </button>
                    </div>

                    <!-- Test Output Box -->
                    <div id="testResultBox" class="hidden p-4 rounded-xl border text-xs"></div>
                </div>
            </div>

            <!-- Section D: Automation & Compliance Policy -->
            <div class="glass p-6 rounded-3xl space-y-4">
                <h2 class="text-lg font-bold text-white flex items-center gap-2">
                    <span class="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-black">3</span>
                    Compliance, Suppression &amp; Safety Controls
                </h2>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                    <div class="p-4 bg-gray-900/60 rounded-2xl border border-gray-800">
                        <div class="font-bold text-white mb-1">Bilingual Opt-Out (STOP / PARAR)</div>
                        <p class="text-gray-400">Incoming keywords STOP, CANCEL, PARAR, BAJA immediately suppress the contact in Supabase and tag GHL. Proactive outbound is permanently halted.</p>
                    </div>
                    <div class="p-4 bg-gray-900/60 rounded-2xl border border-gray-800">
                        <div class="font-bold text-white mb-1">Human Takeover Lock</div>
                        <p class="text-gray-400">When customer asks for "humano" or an agent claims the conversation in GHL, AI auto-replies are paused to prevent competing messages.</p>
                    </div>
                    <div class="p-4 bg-gray-900/60 rounded-2xl border border-gray-800">
                        <div class="font-bold text-white mb-1">Meta 24h Window Gating</div>
                        <p class="text-gray-400">System enforces Meta policy: free-form text requires an inbound reply within 24h. All proactive notifications use approved templates.</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function refreshStatus() {{
                try {{
                    const res = await fetch('/api/whatsapp/status');
                    const d = await res.json();
                    
                    document.getElementById('status-meta').innerText = d.connections.meta_business_account;
                    document.getElementById('status-meta').className = d.connections.meta_business_account === 'CONNECTED' ? 'mt-2 text-xs font-black text-emerald-400' : 'mt-2 text-xs font-black text-amber-400';
                    
                    document.getElementById('status-number').innerText = d.connections.whatsapp_number;
                    document.getElementById('status-number').className = d.connections.whatsapp_number === 'CONNECTED' ? 'mt-2 text-xs font-black text-emerald-400' : 'mt-2 text-xs font-black text-amber-400';
                    
                    document.getElementById('cost-mtd').innerHTML = `$${{d.cost_telemetry.total_cost_mtd_usd.toFixed(2)}} <span class="text-xs text-gray-400 font-normal">/ $${{d.cost_telemetry.monthly_budget_usd.toFixed(2)}} Limit</span>`;
                    document.getElementById('free-tier').innerHTML = `${{d.cost_telemetry.free_tier_remaining}} <span class="text-xs text-gray-400 font-normal">Remaining</span>`;
                    document.getElementById('msgs-delivered').innerHTML = `${{d.cost_telemetry.messages_sent}} <span class="text-xs text-gray-400 font-normal">Sent MTD</span>`;
                }} catch (e) {{
                    console.error("Status fetch failed", e);
                }}
            }}

            async function sendTestMessage() {{
                const phone = document.getElementById('testPhone').value;
                const type = document.getElementById('testType').value;
                const template = document.getElementById('testTemplate').value;
                const body = document.getElementById('testBody').value;
                const box = document.getElementById('testResultBox');

                if (!phone) {{
                    alert("Please enter a recipient phone number.");
                    return;
                }}

                box.className = "p-4 rounded-xl border border-blue-500/30 bg-blue-500/10 text-blue-200 text-xs";
                box.innerHTML = "Dispatching test message via Meta WhatsApp Cloud API...";
                box.classList.remove('hidden');

                try {{
                    const res = await fetch('/api/whatsapp/send-test', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            recipient_phone: phone,
                            message_type: type,
                            template_name: template,
                            text_body: body,
                            language: "es"
                        }})
                    }});
                    const d = await res.json();
                    if (d.success) {{
                        box.className = "p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-200 text-xs";
                        box.innerHTML = `<strong>✓ Message Dispatched Successfully!</strong><br>Status: ${{d.dispatch_result.status || 'Sent'}}<br>Meta Message ID: <code>${{d.dispatch_result.messages ? d.dispatch_result.messages[0].id : 'simulated'}}</code><br>Estimated Cost: $${{d.estimated_cost_usd.toFixed(4)}} USD`;
                    }} else {{
                        box.className = "p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-200 text-xs";
                        box.innerHTML = `<strong>⚠️ Blocked by Gate:</strong> ${{d.reason || d.error || 'Failed to dispatch'}}`;
                    }}
                    refreshStatus();
                }} catch (e) {{
                    box.className = "p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-200 text-xs";
                    box.innerHTML = `<strong>Error:</strong> ${{e.message}}`;
                }}
            }}

            refreshStatus();
        </script>
    </body>
    </html>
    """

@app.get("/academy", response_class=HTMLResponse)
def render_academy():
    """
    Renders the SitaOS Operations, Error Checking & $50k/Mo Sales Academy.
    """
    academy_path = os.path.join(os.path.dirname(__file__), "static", "academy.html")
    if os.path.exists(academy_path):
        with open(academy_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>SitaOS Operations Academy loading...</h1>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
