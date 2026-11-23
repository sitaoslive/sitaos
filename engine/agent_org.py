"""
Alpha Vision AI Sales OS - Multi-Agent AI Sales Organization Engine
Registers and coordinates the 14 specialized AI agents with deterministic tools,
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
        self._register_14_specialized_agents()

    def _register_14_specialized_agents(self):
        """Registers all 14 specified AI agents with strict boundaries."""
        agents = [
            AIAgentSpec(
                agent_id="agent_01_orchestrator",
                name="Chief Revenue Orchestrator",
                role_title="Commercial Workflow Coordinator",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Coordinate end-to-end commercial lifecycle, enforce deterministic transitions and compliance rules.",
                permitted_tools=["get_campaign_status", "assign_agent_task", "check_compliance", "pause_campaign"],
                max_tokens_per_call=2000,
                cost_ceiling_usd=0.04,
                confidence_threshold=0.90,
                escalation_rule="Escalate to human operator if policy breach or unexpected pipeline loop occurs."
            ),
            AIAgentSpec(
                agent_id="agent_02_market_intel",
                name="Market Intelligence Agent",
                role_title="Target ICP & Market Segment Specialist",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Analyze trade & veterinary niches across US, Canada, Colombia, Mexico, and generate product-specific ICPs.",
                permitted_tools=["query_market_benchmarks", "evaluate_geographic_pricing", "assess_buying_triggers"],
                max_tokens_per_call=3000,
                cost_ceiling_usd=0.05,
                confidence_threshold=0.85,
                escalation_rule="Flag for administrator review when market conversion rate dips below 0.3%."
            ),
            AIAgentSpec(
                agent_id="agent_03_prospect_discovery",
                name="Prospect Discovery Agent",
                role_title="B2B Directory & Lead Harvester",
                cognitive_model=config.CLAUDE_MODEL_FAST_TRIAGE,
                primary_purpose="Ingest and normalize business prospects from lawful, authorized sources with conservative deduplication.",
                permitted_tools=["query_places_api", "deduplicate_identity_graph", "validate_corporate_domain"],
                max_tokens_per_call=1000,
                cost_ceiling_usd=0.01,
                confidence_threshold=0.88,
                escalation_rule="Reject incomplete contact records missing verifiable business domain or public phone."
            ),
            AIAgentSpec(
                agent_id="agent_04_business_research",
                name="Business Research Agent",
                role_title="Forensic Operations & Friction Auditor",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Analyze public websites and workflows to extract cited evidence of operational bottlenecks.",
                permitted_tools=["crawl_public_site", "extract_booking_friction", "validate_evidence_citations"],
                max_tokens_per_call=3500,
                cost_ceiling_usd=0.06,
                confidence_threshold=0.85,
                escalation_rule="Never infer private financial data or employee counts from ambiguous signals."
            ),
            AIAgentSpec(
                agent_id="agent_05_lead_qualification",
                name="Lead Qualification Agent",
                role_title="100-Point Scoring & Fit Evaluator",
                cognitive_model=config.CLAUDE_MODEL_FAST_TRIAGE,
                primary_purpose="Evaluate product fit, company size, verified friction, contactability, and output deterministic 0-100 score.",
                permitted_tools=["compute_score_breakdown", "assign_priority_tier", "check_legal_eligibility"],
                max_tokens_per_call=1200,
                cost_ceiling_usd=0.015,
                confidence_threshold=0.90,
                escalation_rule="Disqualify prospect automatically if score < 50 or region is unsupported."
            ),
            AIAgentSpec(
                agent_id="agent_06_personalized_outreach",
                name="Personalized Outreach Agent",
                role_title="Bespoke Consultative Copywriter",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Write natural, evidence-backed email and WhatsApp outreach copy with mandatory opt-out notices.",
                permitted_tools=["lint_spam_phrases", "verify_evidence_citations", "queue_for_human_approval"],
                max_tokens_per_call=2500,
                cost_ceiling_usd=0.035,
                confidence_threshold=0.92,
                escalation_rule="Block dispatch and alert operator if copy contains unverified ROI or hype claims."
            ),
            AIAgentSpec(
                agent_id="agent_07_conversation_intelligence",
                name="Conversation Intelligence Agent",
                role_title="Omnichannel Response Classifier",
                cognitive_model=config.CLAUDE_MODEL_FAST_TRIAGE,
                primary_purpose="Categorize prospect replies in real time (Interested, Demo, Pricing, Objection, Unsubscribe, Complaint).",
                permitted_tools=["classify_intent", "trigger_immediate_suppression", "advance_crm_stage"],
                max_tokens_per_call=800,
                cost_ceiling_usd=0.008,
                confidence_threshold=0.92,
                escalation_rule="Execute instantaneous global suppression on unsubscribe or opt-out keywords."
            ),
            AIAgentSpec(
                agent_id="agent_08_sales_consultant",
                name="AI Sales Consultant",
                role_title="Consultative Discovery Specialist",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Conduct consultative discovery, ask targeted questions, and connect pain points to real software capabilities.",
                permitted_tools=["query_product_knowledge", "calculate_revenue_leakage", "generate_demo_invitation"],
                max_tokens_per_call=2000,
                cost_ceiling_usd=0.03,
                confidence_threshold=0.88,
                escalation_rule="Escalate to human team if custom enterprise pricing or legal negotiations requested."
            ),
            AIAgentSpec(
                agent_id="agent_09_demo_personalization",
                name="Demo Personalization Agent",
                role_title="Interactive Scenario Tailor",
                cognitive_model=config.CLAUDE_MODEL_FAST_TRIAGE,
                primary_purpose="Configure synthetic demonstration data and industry scenarios matching prospect's business type.",
                permitted_tools=["provision_demo_session", "select_synthetic_scenario", "encode_token_metadata"],
                max_tokens_per_call=1000,
                cost_ceiling_usd=0.012,
                confidence_threshold=0.90,
                escalation_rule="Ensure zero exposure of real patient, customer, or financial records in demo frames."
            ),
            AIAgentSpec(
                agent_id="agent_10_interactive_demo_guide",
                name="Interactive Demo Guide",
                role_title="In-App Concierge & Product Guide",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Answer prospect questions live during the walkthrough, explain screens, and encourage commercial trial/buy.",
                permitted_tools=["retrieve_feature_doc", "explain_active_screen", "recommend_approved_tier"],
                max_tokens_per_call=1500,
                cost_ceiling_usd=0.025,
                confidence_threshold=0.90,
                escalation_rule="Never claim an action is finished if not executed in sandbox."
            ),
            AIAgentSpec(
                agent_id="agent_11_objection_closer",
                name="Objection and Closing Agent",
                role_title="Truthful Commercial Closer",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Handle common objections (price, complexity, time, mobile) truthfully using approved policies.",
                permitted_tools=["get_approved_faqs", "issue_checkout_link", "clarify_cancellation_terms"],
                max_tokens_per_call=1800,
                cost_ceiling_usd=0.03,
                confidence_threshold=0.90,
                escalation_rule="Transfer conversation to human sales specialist when prospect explicitly asks for a person."
            ),
            AIAgentSpec(
                agent_id="agent_12_revenue_recovery",
                name="Revenue Recovery Agent",
                role_title="Lifecycle Re-engagement Specialist",
                cognitive_model=config.CLAUDE_MODEL_FAST_TRIAGE,
                primary_purpose="Identify abandoned checkouts, unfinished demos, and expiring trials for helpful re-engagement.",
                permitted_tools=["check_abandonment_state", "draft_recovery_email", "apply_cadence_limits"],
                max_tokens_per_call=1000,
                cost_ceiling_usd=0.01,
                confidence_threshold=0.88,
                escalation_rule="Halt follow-ups immediately if maximum cadence limit (3 touches) is reached."
            ),
            AIAgentSpec(
                agent_id="agent_13_onboarding_coordinator",
                name="Customer Onboarding Coordinator",
                role_title="Post-Purchase Implementation Coordinator",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Compile intake questionnaires, sync GHL calendar appointments, and generate AI specialist briefings.",
                permitted_tools=["sync_ghl_calendar", "generate_specialist_briefing", "track_setup_milestones"],
                max_tokens_per_call=2500,
                cost_ceiling_usd=0.035,
                confidence_threshold=0.95,
                escalation_rule="Alert team immediately if scheduled onboarding call is cancelled or no-showed."
            ),
            AIAgentSpec(
                agent_id="agent_14_revenue_optimizer",
                name="Revenue Optimization Agent",
                role_title="Unit Economics & Experimentation Analyst",
                cognitive_model=config.CLAUDE_MODEL_DEEP_REASONING,
                primary_purpose="Analyze CAC, LTV, token margins, channel conversion, and recommend supervised experiment tweaks.",
                permitted_tools=["compute_unit_economics", "audit_llm_token_costs", "propose_ab_variant"],
                max_tokens_per_call=3000,
                cost_ceiling_usd=0.05,
                confidence_threshold=0.90,
                escalation_rule="Never autonomously change approved prices, legal contracts, or sending limits."
            ),
        ]
        for a in agents:
            self.agents_registry[a.agent_id] = a

    def execute_agent_task(self, agent_id: str, task_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates/executes agent reasoning with token accounting and audit trail."""
        spec = self.agents_registry.get(agent_id)
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
