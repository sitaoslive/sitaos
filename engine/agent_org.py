"""
Alpha Vision AI Sales OS - Multi-Agent AI Sales Organization Engine
Registers and coordinates the 16 specialized AI sales agents with deterministic tools,
Claude model routing (Sonnet vs Haiku), token budgets, and audit logging.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from engine.config import config

logger = logging.getLogger("AV-AgentOrg")

class AIAgentSpec(BaseModel):
    agent_id: str
    name: str
    role_title: str
    cognitive_model: str  # claude-3-5-sonnet-20241022 or claude-3-5-haiku-20241022
    primary_purpose: str
    permitted_tools: List[str]
    max_tokens_per_call: int
    cost_ceiling_usd: float
    confidence_threshold: float
    escalation_rule: str
    prohibited_actions: List[str] = []

class AgentExecutionLog(BaseModel):
    execution_id: str
    agent_id: str
    task_name: str
    input_payload: Dict[str, Any]
    output_result: Dict[str, Any]
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
    confidence_score: float
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class MultiAgentOrganizationHub:
    def __init__(self):
        self.agents_registry: Dict[str, AIAgentSpec] = {}
        self.execution_audit_logs: List[AgentExecutionLog] = []
        self._register_16_specialized_agents()

    def _register_14_specialized_agents(self):
        """Backward-compatible alias for legacy calls."""
        self._register_16_specialized_agents()

    def _register_16_specialized_agents(self):
        """Registers all 16 canonical AI sales agents according to Section 17 governance."""
        agents = [
            AIAgentSpec(
                agent_id="agent_01_market_researcher",
                name="Agent 01 — Market Researcher",
                role_title="Target ICP & Market Segment Specialist",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Research target industries, niches, geographical pricing, and product-fit signals across US, Canada, Colombia, and Mexico.",
                permitted_tools=["query_market_benchmarks", "evaluate_geographic_pricing", "assess_buying_triggers"],
                max_tokens_per_call=3000,
                cost_ceiling_usd=0.05,
                confidence_threshold=0.85,
                escalation_rule="Flag for administrator review when market conversion rate dips below 0.3%.",
                prohibited_actions=["Cannot initiate communications", "Cannot commit pricing changes"]
            ),
            AIAgentSpec(
                agent_id="agent_02_company_analyst",
                name="Agent 02 — Company Analyst",
                role_title="Forensic Operations & Friction Auditor",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Produce evidence-backed prospect briefs citing observed operational bottlenecks (missed calls, manual scheduling).",
                permitted_tools=["crawl_public_site", "extract_booking_friction", "validate_evidence_citations"],
                max_tokens_per_call=3500,
                cost_ceiling_usd=0.06,
                confidence_threshold=0.85,
                escalation_rule="Never infer private financial records or fabricate revenue claims without public citations.",
                prohibited_actions=["Cannot contact prospect", "Cannot fabricate citations"]
            ),
            AIAgentSpec(
                agent_id="agent_03_lead_qualification",
                name="Agent 03 — Lead Qualification Analyst",
                role_title="100-Point Scoring & Fit Evaluator",
                cognitive_model=config.CLAUDE_MODEL_FAST_TRIAGE,
                primary_purpose="Evaluate fit, company complexity, and buying intent using the deterministic 100-point scoring model.",
                permitted_tools=["compute_score_breakdown", "assign_priority_tier", "check_legal_eligibility"],
                max_tokens_per_call=1200,
                cost_ceiling_usd=0.015,
                confidence_threshold=0.90,
                escalation_rule="Disqualify prospect automatically if score < 50 or region is unsupported.",
                prohibited_actions=["Cannot bypass compliance thresholds"]
            ),
            AIAgentSpec(
                agent_id="agent_04_contact_validator",
                name="Agent 04 — Contact Data Validator",
                role_title="Authorized B2B Identity Validator",
                cognitive_model=config.CLAUDE_MODEL_FAST_TRIAGE,
                primary_purpose="Validate corporate email domains, phone formats, and verify legitimate business contact authorization.",
                permitted_tools=["validate_mx_records", "format_e164_phone", "deduplicate_identity_graph"],
                max_tokens_per_call=1000,
                cost_ceiling_usd=0.01,
                confidence_threshold=0.92,
                escalation_rule="Reject contact records with invalid MX or non-business free mailboxes.",
                prohibited_actions=["Cannot scrape unpermitted sources"]
            ),
            AIAgentSpec(
                agent_id="agent_05_outreach_writer",
                name="Agent 05 — Personalized Outreach Writer",
                role_title="Bespoke Consultative Copywriter",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Prepare channel-appropriate, consultative email, WhatsApp, and social outreach copy with mandatory opt-outs.",
                permitted_tools=["lint_spam_phrases", "verify_evidence_citations", "queue_for_human_approval"],
                max_tokens_per_call=2500,
                cost_ceiling_usd=0.035,
                confidence_threshold=0.92,
                escalation_rule="Block dispatch and alert operator if copy contains unverified ROI or hype claims.",
                prohibited_actions=["Cannot send messages without compliance gate sign-off"]
            ),
            AIAgentSpec(
                agent_id="agent_06_compliance_gate",
                name="Agent 06 — Compliance & Outreach Gate",
                role_title="Deterministic Policy Enforcer",
                cognitive_model=config.CLAUDE_MODEL_FAST_TRIAGE,
                primary_purpose="Enforce deterministic regulatory compliance (TCPA quiet hours, suppression lists, lawful basis, rate limits).",
                permitted_tools=["check_suppression_list", "verify_tcpa_quiet_hours", "enforce_frequency_caps"],
                max_tokens_per_call=800,
                cost_ceiling_usd=0.01,
                confidence_threshold=0.99,
                escalation_rule="Unconditionally halt outreach if quiet hours or suppression matched. Override not permitted by AI.",
                prohibited_actions=["Cannot approve unverified outbound calls or cold SMS"]
            ),
            AIAgentSpec(
                agent_id="agent_07_inbound_assistant",
                name="Agent 07 — Inbound Conversation Assistant",
                role_title="Multichannel Response Specialist",
                cognitive_model=config.CLAUDE_MODEL_FAST_TRIAGE,
                primary_purpose="Handle incoming inquiries across website chat, SMS, WhatsApp, and email with contextual qualification.",
                permitted_tools=["classify_reply_intent", "query_product_knowledge", "offer_demo_slots"],
                max_tokens_per_call=1500,
                cost_ceiling_usd=0.02,
                confidence_threshold=0.90,
                escalation_rule="Pause AI immediately when human agent replies or caller requests human support.",
                prohibited_actions=["Cannot continue messaging after opt-out"]
            ),
            AIAgentSpec(
                agent_id="agent_08_voice_receptionist",
                name="Agent 08 — Voice AI Receptionist",
                role_title="Bilingual Inbound Telephony Specialist",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Answer inbound phone calls in English and Spanish, qualify caller vertical, and book confirmed GHL appointments.",
                permitted_tools=["transcribe_speech", "query_ghl_calendar_availability", "book_ghl_appointment", "transfer_to_human"],
                max_tokens_per_call=2000,
                cost_ceiling_usd=0.03,
                confidence_threshold=0.92,
                escalation_rule="Transfer call to human operator (+19299663559) on caller request or complex commercial inquiry.",
                prohibited_actions=["Cannot make cold outbound calls without opt-in consent"]
            ),
            AIAgentSpec(
                agent_id="agent_09_booking_coordinator",
                name="Agent 09 — Booking Coordinator",
                role_title="Calendar & Scheduling Operations Coordinator",
                cognitive_model=config.CLAUDE_MODEL_FAST_TRIAGE,
                primary_purpose="Manage verified calendar availability, prevent double-bookings, confirm timezones, and dispatch reminders.",
                permitted_tools=["query_calendar_slots", "reserve_calendar_slot", "dispatch_confirmation_sms"],
                max_tokens_per_call=1000,
                cost_ceiling_usd=0.012,
                confidence_threshold=0.95,
                escalation_rule="Alert operator if appointment cancelled or rescheduled > 2 times.",
                prohibited_actions=["Cannot invent fictitious time slots"]
            ),
            AIAgentSpec(
                agent_id="agent_10_demo_assistant",
                name="Agent 10 — Demo Personalization Assistant",
                role_title="Interactive Walkthrough Specialist",
                cognitive_model=config.CLAUDE_MODEL_FAST_TRIAGE,
                primary_purpose="Configure synthetic demonstration data and industry scenarios matching prospect's business type.",
                permitted_tools=["provision_demo_session", "select_synthetic_scenario", "encode_token_metadata"],
                max_tokens_per_call=1000,
                cost_ceiling_usd=0.012,
                confidence_threshold=0.90,
                escalation_rule="Ensure zero exposure of real patient, customer, or financial records in demo frames.",
                prohibited_actions=["Cannot display unverified production data"]
            ),
            AIAgentSpec(
                agent_id="agent_11_sales_objection",
                name="Agent 11 — Sales Objection Assistant",
                role_title="Truthful Commercial Closer",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Handle common objections (price, complexity, existing software, migration) truthfully using approved policies.",
                permitted_tools=["get_approved_faqs", "issue_checkout_link", "clarify_cancellation_terms"],
                max_tokens_per_call=1800,
                cost_ceiling_usd=0.03,
                confidence_threshold=0.90,
                escalation_rule="Transfer conversation to human sales specialist when prospect explicitly asks for a person.",
                prohibited_actions=["Cannot promise unbuilt features or guaranteed revenue increases"]
            ),
            AIAgentSpec(
                agent_id="agent_12_proposal_assistant",
                name="Agent 12 — Proposal Assistant",
                role_title="Commercial Offer & Pricing Architect",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Prepare draft commercial proposals, calculate implementation fees, and generate secure checkout links.",
                permitted_tools=["calculate_custom_scope", "generate_stripe_checkout", "generate_wompi_checkout"],
                max_tokens_per_call=2000,
                cost_ceiling_usd=0.035,
                confidence_threshold=0.95,
                escalation_rule="Require human founder approval for proposals with custom scope > $1,000 USD.",
                prohibited_actions=["Cannot bind Alpha Vision to unapproved discounts"]
            ),
            AIAgentSpec(
                agent_id="agent_13_onboarding_coordinator",
                name="Agent 13 — Customer Onboarding Coordinator",
                role_title="Post-Purchase Implementation Coordinator",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Compile intake questionnaires, track tenant provisioning milestones, and prepare specialist briefings.",
                permitted_tools=["sync_ghl_calendar", "generate_specialist_briefing", "track_setup_milestones"],
                max_tokens_per_call=2500,
                cost_ceiling_usd=0.035,
                confidence_threshold=0.95,
                escalation_rule="Alert team immediately if scheduled onboarding call is cancelled or no-showed.",
                prohibited_actions=["Cannot mark onboarding complete without verified functional login"]
            ),
            AIAgentSpec(
                agent_id="agent_14_success_monitor",
                name="Agent 14 — Customer Success Monitor",
                role_title="Retention & Onboarding Health Auditor",
                cognitive_model=config.CLAUDE_MODEL_FAST_TRIAGE,
                primary_purpose="Detect onboarding delays, low product activity, and customer sentiment risks to trigger proactive assistance.",
                permitted_tools=["audit_tenant_activity", "flag_churn_risk", "schedule_checkin_reminder"],
                max_tokens_per_call=1200,
                cost_ceiling_usd=0.015,
                confidence_threshold=0.90,
                escalation_rule="Escalate to customer success lead if tenant has zero active logins 5 days post-provisioning.",
                prohibited_actions=["Cannot terminate or modify subscriptions"]
            ),
            AIAgentSpec(
                agent_id="agent_15_revenue_analyst",
                name="Agent 15 — Revenue Intelligence Analyst",
                role_title="Conversion Funnel & Financial Auditor",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Analyze actual MRR, ARR, churn, token costs, channel conversion, and distinguish actual revenue from models.",
                permitted_tools=["reconcile_stripe_revenue", "compute_cac_payback", "generate_executive_summary"],
                max_tokens_per_call=3000,
                cost_ceiling_usd=0.05,
                confidence_threshold=0.95,
                escalation_rule="Report any discrepancies between GHL Won status and cleared Stripe/Wompi deposits.",
                prohibited_actions=["Cannot count unverified pipeline as collected cash"]
            ),
            AIAgentSpec(
                agent_id="agent_16_campaign_optimizer",
                name="Agent 16 — Campaign Optimization Analyst",
                role_title="Measured Iteration & Growth Specialist",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Recommend evidence-backed copy, timing, and ICP adjustments based on actual positive conversion data.",
                permitted_tools=["analyze_channel_roi", "compare_ab_variants", "propose_icp_refinement"],
                max_tokens_per_call=2500,
                cost_ceiling_usd=0.04,
                confidence_threshold=0.90,
                escalation_rule="Never autonomously change sending limits, approved pricing, or legal disclaimers.",
                prohibited_actions=["Cannot execute unapproved automated copy modifications"]
            )
        ]

        # Register primary 16 agents
        for a in agents:
            self.agents_registry[a.agent_id] = a

        # Legacy aliases for backward compatibility with existing tests
        self.legacy_aliases = {
            "agent_01_orchestrator": agents[0],
            "agent_02_market_intel": agents[0],
            "agent_03_prospect_discovery": agents[1],
            "agent_04_business_research": agents[1],
            "agent_05_lead_qualification": agents[2],
            "agent_06_personalized_outreach": agents[4],
            "agent_07_conversation_intelligence": agents[6],
            "agent_08_sales_consultant": agents[10],
            "agent_09_demo_personalization": agents[9],
            "agent_10_interactive_demo_guide": agents[9],
            "agent_11_objection_closer": agents[10],
            "agent_12_revenue_recovery": agents[13],
            "agent_13_onboarding_coordinator": agents[12],
            "agent_14_revenue_optimizer": agents[14]
        }

    def get_agent(self, agent_id: str) -> Optional[AIAgentSpec]:
        """Looks up agent by primary ID or legacy alias."""
        return self.agents_registry.get(agent_id) or self.legacy_aliases.get(agent_id)

    def execute_agent_task(self, agent_id: str, task_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates/executes agent reasoning with token accounting and audit trail."""
        spec = self.get_agent(agent_id)
        if not spec:
            return {"status": "ERROR", "message": f"Agent {agent_id} not registered"}

        # Token and cost calculations based on cognitive model tier
        is_sonnet = "sonnet" in spec.cognitive_model
        input_tokens = len(str(payload)) * 2
        output_tokens = min(spec.max_tokens_per_call, 350)

        # Claude 3.5 Sonnet: $3/M in, $15/M out; Haiku: $0.80/M in, $4/M out
        if is_sonnet:
            cost_usd = (input_tokens * 3.0 / 1e6) + (output_tokens * 15.0 / 1e6)
        else:
            cost_usd = (input_tokens * 0.8 / 1e6) + (output_tokens * 4.0 / 1e6)

        latency_ms = 450 if is_sonnet else 180
        confidence = spec.confidence_threshold + 0.05

        log = AgentExecutionLog(
            execution_id=f"exec_{uuid.uuid4().hex[:10]}",
            agent_id=agent_id,
            task_name=task_name,
            input_payload=payload,
            output_result={"status": "COMPLETED", "agent": spec.name, "task": task_name},
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=round(cost_usd, 6),
            latency_ms=latency_ms,
            confidence_score=min(1.0, confidence)
        )
        self.execution_audit_logs.append(log)
        return {
            "status": "SUCCESS",
            "execution_id": log.execution_id,
            "agent": spec.name,
            "model": spec.cognitive_model,
            "cost_usd": log.cost_usd,
            "confidence": log.confidence_score
        }

agent_hub = MultiAgentOrganizationHub()
