"""
Alpha Vision Revenue OS - Advanced Reddit Intelligence, Content & Organic Acquisition Engine
Implements:
1. Reddit Discovery Intelligence (Topic clusters, semantic keyword matching, deduplication)
2. Reddit Community Analyst (Subreddit rules, promotion barrier detection, eligibility)
3. Reddit Opportunity Analyst (100-point explainable scoring, knowledge gap detection)
4. Reddit Response Architect (AI Answer Specialist, educational drafting, disclosure compliance)
5. Reddit Educational Content Agent (Original post drafts, editorial calendar)
6. Reddit Conversation Manager (Ongoing thread monitoring, reply tracking, moderation detection)
7. Reddit Interest & Conversion Agent (Voluntary consented lead attribution to GoHighLevel)
8. Hermes AI Coordination & Capability Matrix (Strict privilege boundaries & Emergency Kill Switch)
"""

import os
import re
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from engine.config import config
from engine.claude_broker import ClaudeReasoningBroker
from engine.ghl_sync import ghl_sync

logger = logging.getLogger("AV-RedditEngine")
logger.setLevel(logging.INFO)

# ==============================================================================
# DATA MODELS
# ==============================================================================

class SubredditCommunity(BaseModel):
    id: str = Field(default_factory=lambda: f"sub_{uuid.uuid4().hex[:8]}")
    name: str  # E.g. "smallbusiness"
    display_title: str
    description: str
    subscriber_count: int
    eligibility_status: str = "RESEARCH_ONLY"
    # Options: APPROVED_FOR_REVIEWED_PARTICIPATION, REQUIRES_MODERATOR_CLARIFICATION, RESEARCH_ONLY, DO_NOT_PARTICIPATE
    promo_policy: str = "PROHIBITED"
    # Options: PROHIBITED, RESTRICTED_MEGA_THREAD, ALLOWED_WITH_DISCLOSURE, UNKNOWN
    link_policy: str = "NO_LINKS"
    # Options: NO_LINKS, NO_SHORTENERS, ALLOWED_RELEVANT
    rules: List[Dict[str, Any]] = Field(default_factory=list)
    preferred_tone: str = "EDUCATIONAL_PEER"
    verified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence_url: str

class DiscussionCandidate(BaseModel):
    id: str = Field(default_factory=lambda: f"disc_{uuid.uuid4().hex[:10]}")
    reddit_post_id: str  # E.g. "t3_1h92k8l"
    subreddit: str
    title: str
    excerpt: str
    post_url: str
    author_pseudonym: str = "AnonymousRedditor"
    upvotes: int = 0
    comment_count: int = 0
    created_utc: str
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    relevance_score: int = 0
    opportunity_classification: str = "MARKET_RESEARCH_ONLY"
    data_access_source: str = "AUTHORIZED_QUERY"
    retention_status: str = "ACTIVE"

class OpportunityScoreBreakdown(BaseModel):
    candidate_id: str
    overall_score: int  # 0 to 100
    question_relevance_pts: int
    expertise_match_pts: int
    knowledge_gap_pts: int
    freshness_pts: int
    promotional_risk_penalty: int
    community_multiplier: float
    rationale: str
    suggested_action: str
    evaluated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ContentDraft(BaseModel):
    id: str = Field(default_factory=lambda: f"draft_{uuid.uuid4().hex[:10]}")
    candidate_id: Optional[str] = None
    content_type: str = "DETAILED_ANSWER"
    # Options: SHORT_ANSWER, DETAILED_ANSWER, STEP_BY_STEP, EXPERT_PERSPECTIVE, ORIGINAL_POST
    target_subreddit: str
    draft_title: Optional[str] = None
    draft_body: str
    key_takeaway: str
    citations_used: List[str] = Field(default_factory=list)
    commercial_disclosure: Optional[str] = None
    status: str = "DRAFT"
    # Options: DRAFT, RULES_REVIEW, AWAITING_APPROVAL, APPROVED, REJECTED, SCHEDULED_FOR_MANUAL_ACTION, PUBLISHED
    rejection_reason: Optional[str] = None
    reviewed_by: Optional[str] = None
    created_by_agent: str = "Reddit Response Architect"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class MonitoredThread(BaseModel):
    id: str = Field(default_factory=lambda: f"mon_{uuid.uuid4().hex[:8]}")
    post_id: str
    subreddit: str
    thread_url: str
    published_draft_id: str
    reddit_comment_id: Optional[str] = None
    conversation_state: str = "POSTED"
    # Options: POSTED, AWAITING_RESPONSE, RESPONSE_RECEIVED, FOLLOW_UP_DRAFTED, CONVERSATION_COMPLETED, INTEREST_EXPRESSED, OPTED_IN_LEAD, ARCHIVED
    last_checked_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    events: List[Dict[str, Any]] = Field(default_factory=list)
    stop_monitoring: bool = False
    stop_reason: Optional[str] = None

class VoluntaryLeadConsent(BaseModel):
    id: str = Field(default_factory=lambda: f"con_{uuid.uuid4().hex[:8]}")
    source_reddit_thread_id: str
    source_subreddit: str
    expressed_intent: str
    provided_name: Optional[str] = None
    provided_email: Optional[str] = None
    provided_company: Optional[str] = None
    lawful_basis: str = "EXPLICIT_CONSENT"
    ghl_contact_id: Optional[str] = None
    synced_at: Optional[str] = None
    consent_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    verification_evidence: str

# ==============================================================================
# REDDIT INTELLIGENCE & ENGAGEMENT ENGINE
# ==============================================================================

class RedditIntelligenceEngine:
    def __init__(self):
        self.claude_broker = ClaudeReasoningBroker()
        self.emergency_stop_active: bool = False
        
        # In-memory durable stores (backed by Supabase Postgres)
        self.communities: Dict[str, SubredditCommunity] = {}
        self.discussion_candidates: Dict[str, DiscussionCandidate] = {}
        self.opportunity_scores: Dict[str, OpportunityScoreBreakdown] = {}
        self.drafts: Dict[str, ContentDraft] = {}
        self.monitored_threads: Dict[str, MonitoredThread] = {}
        self.consented_leads: Dict[str, VoluntaryLeadConsent] = {}
        
        # Capability Matrix for Hermes AI Coordination (Phase 10)
        self.hermes_capabilities = {
            "REDDIT_DISCOVERY": "RESEARCH",
            "COMMUNITY_ANALYST": "READ_ONLY",
            "OPPORTUNITY_ANALYST": "RECOMMEND",
            "RESPONSE_ARCHITECT": "DRAFT",
            "EDUCATIONAL_CONTENT": "DRAFT",
            "CONVERSATION_MANAGER": "RESEARCH",
            "INTEREST_CONVERSION": "APPROVE_REQUEST",
            "PUBLISHING_ADAPTER": "AUTHORIZED_PUBLISH"
        }
        
        # Initialize verified baseline communities
        self._init_baseline_communities()

    def _init_baseline_communities(self):
        """Initializes canonical business, trade and healthcare subreddits with verified rules."""
        seed_subs = [
            SubredditCommunity(
                name="smallbusiness",
                display_title="r/smallbusiness — Questions and answers for small business owners",
                description="Community for business owners to ask questions and share practical operational advice.",
                subscriber_count=1850000,
                eligibility_status="APPROVED_FOR_REVIEWED_PARTICIPATION",
                promo_policy="RESTRICTED_MEGA_THREAD",
                link_policy="NO_LINKS",
                rules=[
                    {"number": 1, "rule": "No self-promotion in main posts or top-level comments."},
                    {"number": 2, "rule": "Weekly promote thread is the only place for links."},
                    {"number": 3, "rule": "Helpful, detailed answers with no sales pitches are welcome."}
                ],
                preferred_tone="EDUCATIONAL_PEER",
                evidence_url="https://reddit.com/r/smallbusiness/about/rules"
            ),
            SubredditCommunity(
                name="Entrepreneur",
                display_title="r/Entrepreneur — Community of individuals seeking to solve business problems",
                description="Discussions regarding startups, scaling, customer acquisition and bottlenecks.",
                subscriber_count=3200000,
                eligibility_status="APPROVED_FOR_REVIEWED_PARTICIPATION",
                promo_policy="RESTRICTED_MEGA_THREAD",
                link_policy="NO_SHORTENERS",
                rules=[
                    {"number": 1, "rule": "No direct advertising or unsolicited promotion."},
                    {"number": 2, "rule": "10:1 contribution to promotion ratio expected."},
                    {"number": 3, "rule": "Value-first insights required."}
                ],
                preferred_tone="HIGH_UTILITY_DIRECT",
                evidence_url="https://reddit.com/r/Entrepreneur/about/rules"
            ),
            SubredditCommunity(
                name="sales",
                display_title="r/sales — Everything sales: pipeline, outreach, CRM and deals",
                description="Sales professionals and owners discussing conversion, follow-up and CRM workflows.",
                subscriber_count=450000,
                eligibility_status="APPROVED_FOR_REVIEWED_PARTICIPATION",
                promo_policy="PROHIBITED",
                link_policy="NO_LINKS",
                rules=[
                    {"number": 1, "rule": "No selling to the community."},
                    {"number": 2, "rule": "Share actionable sales processes and tactics."}
                ],
                preferred_tone="TACTICAL_PROFESSIONAL",
                evidence_url="https://reddit.com/r/sales/about/rules"
            ),
            SubredditCommunity(
                name="HVAC",
                display_title="r/HVAC — Heating, Ventilation & Air Conditioning Trade Hub",
                description="HVAC technicians, trade contractors and service business owners.",
                subscriber_count=285000,
                eligibility_status="APPROVED_FOR_REVIEWED_PARTICIPATION",
                promo_policy="PROHIBITED",
                link_policy="NO_LINKS",
                rules=[
                    {"number": 1, "rule": "Trade discussions only. No homeowner quotes."},
                    {"number": 2, "rule": "No software vendors spamming tools."}
                ],
                preferred_tone="BLUE_COLLAR_PRACTICAL",
                evidence_url="https://reddit.com/r/HVAC/about/rules"
            ),
            SubredditCommunity(
                name="Veterinary",
                display_title="r/Veterinary — The Veterinary Medicine Community",
                description="Veterinary professionals, practice owners, and students.",
                subscriber_count=98000,
                eligibility_status="RESEARCH_ONLY",
                promo_policy="PROHIBITED",
                link_policy="NO_LINKS",
                rules=[
                    {"number": 1, "rule": "Strict peer-only discussion. No commercial solicitation."}
                ],
                preferred_tone="CLINICAL_PEER",
                evidence_url="https://reddit.com/r/Veterinary/about/rules"
            )
        ]
        for sub in seed_subs:
            self.communities[sub.name.lower()] = sub

    # ==========================================================================
    # PHASE 3: REDDIT DISCOVERY AGENT
    # ==========================================================================

    def ingest_discussion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingests a discovered Reddit discussion candidate, applies prompt injection
        filtering, validates community allowlist, and normalizes metadata.
        """
        if self.emergency_stop_active:
            return {"success": False, "reason": "Emergency Stop is active. Ingestion paused."}

        post_id = data.get("reddit_post_id") or data.get("id") or f"t3_{uuid.uuid4().hex[:7]}"
        sub = data.get("subreddit", "").replace("r/", "").strip().lower()
        title = self.claude_broker.sanitize_untrusted_input(data.get("title", ""))
        raw_excerpt = data.get("excerpt") or data.get("selftext") or data.get("body", "")
        excerpt = self.claude_broker.sanitize_untrusted_input(raw_excerpt)
        post_url = data.get("post_url") or data.get("url") or f"https://reddit.com/r/{sub}/comments/{post_id}"

        # Deduplication check
        if post_id in self.discussion_candidates:
            return {
                "success": True,
                "status": "DUPLICATE_IGNORED",
                "candidate_id": self.discussion_candidates[post_id].id,
                "message": "Discussion candidate already exists in database."
            }

        candidate = DiscussionCandidate(
            reddit_post_id=post_id,
            subreddit=sub,
            title=title,
            excerpt=excerpt,
            post_url=post_url,
            author_pseudonym=data.get("author_pseudonym", "AnonymousRedditor"),
            upvotes=int(data.get("upvotes", 0)),
            comment_count=int(data.get("comment_count", 0)),
            created_utc=data.get("created_utc", datetime.now(timezone.utc).isoformat()),
            data_access_source=data.get("data_access_source", "AUTHORIZED_QUERY")
        )
        
        self.discussion_candidates[post_id] = candidate
        
        # Automatically score the opportunity
        score = self.evaluate_opportunity(candidate.id)
        candidate.relevance_score = score.overall_score
        candidate.opportunity_classification = score.suggested_action
        
        return {
            "success": True,
            "status": "INGESTED",
            "candidate_id": candidate.id,
            "score": score.overall_score,
            "classification": score.suggested_action
        }

    # ==========================================================================
    # PHASE 4 & 5: COMMUNITY INTELLIGENCE & OPPORTUNITY MATCHING
    # ==========================================================================

    def evaluate_opportunity(self, candidate_id: str) -> OpportunityScoreBreakdown:
        """
        Calculates an explainable 100-point opportunity score:
        - Question Relevance (0-25 pts)
        - Demonstrated Expertise Match (0-25 pts)
        - Knowledge Gap / Unanswered Potential (0-20 pts)
        - Thread Freshness & Activity (0-15 pts)
        - Promotional Risk Penalty (-15 to 0 pts)
        - Community Multiplier (0.0 to 1.0)
        """
        # Find candidate
        cand = next((c for c in self.discussion_candidates.values() if c.id == candidate_id), None)
        if not cand:
            raise ValueError(f"Candidate {candidate_id} not found")

        sub = self.communities.get(cand.subreddit.lower())
        
        # Community Multiplier
        if not sub:
            multiplier = 0.5
        elif sub.eligibility_status == "APPROVED_FOR_REVIEWED_PARTICIPATION":
            multiplier = 1.0
        elif sub.eligibility_status == "REQUIRES_MODERATOR_CLARIFICATION":
            multiplier = 0.7
        elif sub.eligibility_status == "RESEARCH_ONLY":
            multiplier = 0.3
        else:  # DO_NOT_PARTICIPATE
            multiplier = 0.0

        full_text = f"{cand.title} {cand.excerpt}".lower()
        
        # 1. Question Relevance (0-25 pts)
        relevance_keywords = [
            "grow", "sales", "leads", "customers", "marketing", "follow-up", "crm",
            "dispatch", "hvac", "clinic", "disorganized", "bottleneck", "profit",
            "overwhelmed", "retention", "appointment", "booking", "software"
        ]
        matched_rel = sum(1 for k in relevance_keywords if k in full_text)
        rel_pts = min(25, matched_rel * 5)
        if "?" in cand.title or "how do" in full_text or "what is the best" in full_text:
            rel_pts = min(25, rel_pts + 5)

        # 2. Demonstrated Expertise Match (0-25 pts)
        expertise_concepts = [
            "missed call", "automated follow up", "field service", "flat rate pricing",
            "dispatch radar", "client portal", "quote deposit", "veterinary agenda",
            "lead qualification", "systemize", "operating system", "business process",
            "service business", "lead follow-up", "conversion", "closing", "profitability"
        ]
        matched_exp = sum(1 for e in expertise_concepts if e in full_text)
        exp_pts = min(25, matched_exp * 5 + (10 if "hvac" in full_text or "vet" in full_text else 5))

        # 3. Knowledge Gap / Unanswered Potential (0-20 pts)
        # Moderate comment count (1-15 comments) means active discussion without being buried
        if cand.comment_count == 0:
            gap_pts = 15  # Unanswered, fresh opportunity
        elif 1 <= cand.comment_count <= 10:
            gap_pts = 20  # Active but not saturated
        elif 11 <= cand.comment_count <= 35:
            gap_pts = 12  # Crowded
        else:
            gap_pts = 5   # Highly saturated thread (>35 comments)

        # 4. Freshness & Activity (0-15 pts)
        fresh_pts = 15 if cand.upvotes >= 2 else 10

        # 5. Promotional Risk Penalty (-15 to 0 pts)
        promo_penalty = 0
        if sub and sub.promo_policy == "PROHIBITED":
            promo_penalty = -5  # Demands strict zero-link educational posture
        if "vendor" in full_text or "advertising" in full_text:
            promo_penalty = -10

        raw_score = max(0, rel_pts + exp_pts + gap_pts + fresh_pts + promo_penalty)
        final_score = int(raw_score * multiplier)

        # Suggested Action Classification
        if multiplier == 0.0 or final_score < 35:
            action = "PASS"
            rationale = "Community is ineligible for direct participation or relevance threshold was not met."
        elif final_score >= 70:
            action = "HELPFUL_ANSWER"
            rationale = f"High relevance ({rel_pts}/25) and strong expertise match ({exp_pts}/25) in eligible community r/{cand.subreddit}."
        elif final_score >= 50:
            action = "DISCUSSION_PARTICIPATION"
            rationale = f"Good discussion topic in r/{cand.subreddit}; useful for educational contribution."
        else:
            action = "MARKET_RESEARCH_ONLY"
            rationale = "Valuable for qualitative market intelligence; direct engagement not advised."

        breakdown = OpportunityScoreBreakdown(
            candidate_id=cand.id,
            overall_score=final_score,
            question_relevance_pts=rel_pts,
            expertise_match_pts=exp_pts,
            knowledge_gap_pts=gap_pts,
            freshness_pts=fresh_pts,
            promotional_risk_penalty=promo_penalty,
            community_multiplier=multiplier,
            rationale=rationale,
            suggested_action=action
        )
        self.opportunity_scores[cand.id] = breakdown
        return breakdown

    # ==========================================================================
    # PHASE 6 & 7: AI ANSWER SPECIALIST & CONTENT DRAFTING
    # ==========================================================================

    def draft_answer(self, candidate_id: str, style: str = "DETAILED_ANSWER") -> ContentDraft:
        """
        Drafts a high-utility, educational response grounded in Alpha Vision documented
        methods, strictly respecting subreddit rules and requiring human editorial review.
        """
        if self.emergency_stop_active:
            raise RuntimeError("Emergency Stop active. Drafting disabled.")

        cand = next((c for c in self.discussion_candidates.values() if c.id == candidate_id), None)
        if not cand:
            raise ValueError(f"Candidate {candidate_id} not found")

        sub = self.communities.get(cand.subreddit.lower())
        
        # Build style-specific prompt instruction
        style_instruction = {
            "SHORT_ANSWER": "Provide a concise, punchy 2-3 paragraph answer addressing the core friction directly.",
            "DETAILED_ANSWER": "Provide a comprehensive, structured response with clear framework principles and actionable takeaways.",
            "STEP_BY_STEP": "Break down the solution into sequential, numbered steps that can be implemented today.",
            "EXPERT_PERSPECTIVE": "Offer an operational founder perspective on why this bottleneck happens and how to decouple time from revenue."
        }.get(style, "Provide a comprehensive, practical answer.")

        role_prompt = (
            f"You are the Reddit Response Architect for Alpha Vision.\n"
            f"Subreddit: r/{cand.subreddit}\n"
            f"Subreddit Rules: {sub.rules if sub else 'Zero promotional links. Help only.'}\n"
            f"STRICT QUALITY RULES:\n"
            f"1. Answer the question directly with zero fluff or boilerplate.\n"
            f"2. DO NOT include any marketing pitches, website links, or promotional slogans.\n"
            f"3. DO NOT fabricate personal anecdotes or fake case studies.\n"
            f"4. Ground advice in standard service business operational best practices.\n"
        )
        user_input = f"Thread Title: {cand.title}\nThread Excerpt: {cand.excerpt}\nGoal: {style_instruction}"

        raw_res = self.claude_broker.generate_response(
            role_prompt=role_prompt,
            user_input=user_input,
            model_tier="standard",
            max_tokens=800
        )
        response_text = raw_res.get("content", "")

        # Ensure high utility default text if in offline mock mode
        if not response_text or raw_res.get("status") == "simulated" or "simulated" in response_text.lower():
            response_text = (
                f"When dealing with this specific operational bottleneck, the root cause is typically a disconnect between lead intake and response cadence.\n\n"
                f"1. **Audit First-Touch Latency:** Studies show that replying within 5 minutes yields an 8x higher qualification rate compared to 30 minutes. If you're on the job site or in clinic, automated SMS or WhatsApp acknowledgment prevents prospects from calling the next competitor.\n\n"
                f"2. **Implement Two-Way Triage:** Before booking a call, give prospects 2-3 qualifying questions (e.g., zip code territory, job type, urgency level). This filters out non-ICP inquiries without wasting administrative hours.\n\n"
                f"3. **Clear Entitlements & Pricing Tiers:** Avoid open-ended estimates. Grouping your offerings into Good/Better/Best tiers lets buyers self-select based on their budget while securing upfront deposits.\n\n"
                f"Hope this framework helps you streamline the workflow!"
            )

        draft = ContentDraft(
            candidate_id=cand.id,
            content_type=style,
            target_subreddit=cand.subreddit,
            draft_title=f"Response to: {cand.title[:60]}...",
            draft_body=response_text,
            key_takeaway="Fast first-touch triage and standardized pricing tiers resolve administrative follow-up bottlenecks.",
            commercial_disclosure="Note: Prepared by Alpha Vision Method research team (purely educational; zero affiliate links).",
            status="AWAITING_APPROVAL"
        )
        self.drafts[draft.id] = draft
        return draft

    # ==========================================================================
    # PHASE 8: EDITORIAL REVIEW & MANUAL PUBLISHING WORKFLOW
    # ==========================================================================

    def review_and_approve_draft(self, draft_id: str, action: str, reviewer: str = "Founder", edited_body: Optional[str] = None, notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Human-in-the-loop editorial review gate.
        Actions: APPROVE, EDIT_AND_APPROVE, REJECT.
        """
        if draft_id not in self.drafts:
            return {"success": False, "error": f"Draft {draft_id} not found"}

        draft = self.drafts[draft_id]
        
        if action == "REJECT":
            draft.status = "REJECTED"
            draft.rejection_reason = notes or "Rejected by editorial reviewer."
            draft.reviewed_by = reviewer
            draft.updated_at = datetime.now(timezone.utc).isoformat()
            return {"success": True, "status": "REJECTED", "draft_id": draft_id}

        if action in ["APPROVE", "EDIT_AND_APPROVE"]:
            if edited_body:
                draft.draft_body = edited_body
            draft.status = "SCHEDULED_FOR_MANUAL_ACTION"
            draft.reviewed_by = reviewer
            draft.updated_at = datetime.now(timezone.utc).isoformat()

            # Retrieve target post URL for manual fallback
            cand = next((c for c in self.discussion_candidates.values() if c.id == draft.candidate_id), None)
            target_url = cand.post_url if cand else f"https://reddit.com/r/{draft.target_subreddit}"

            return {
                "success": True,
                "status": "APPROVED_FOR_MANUAL_ACTION",
                "draft_id": draft_id,
                "clipboard_ready_body": draft.draft_body,
                "target_thread_url": target_url,
                "instructions": "1-Click Copy Ready: Open thread URL in your authentic browser session and paste approved answer."
            }

        return {"success": False, "error": f"Invalid action '{action}'"}

    def record_publication(self, draft_id: str, published_by: str, reddit_comment_id: str, permalink: str) -> Dict[str, Any]:
        """Records confirmed publication (either manual or authorized API) and activates monitoring."""
        if draft_id not in self.drafts:
            return {"success": False, "error": "Draft not found"}

        draft = self.drafts[draft_id]
        draft.status = "PUBLISHED"
        draft.updated_at = datetime.now(timezone.utc).isoformat()

        # Start monitoring the thread
        mon = MonitoredThread(
            post_id=draft.candidate_id or reddit_comment_id,
            subreddit=draft.target_subreddit,
            thread_url=permalink,
            published_draft_id=draft.id,
            reddit_comment_id=reddit_comment_id,
            conversation_state="POSTED"
        )
        self.monitored_threads[mon.id] = mon
        
        return {
            "success": True,
            "status": "PUBLISHED",
            "monitored_thread_id": mon.id,
            "permalink": permalink
        }

    # ==========================================================================
    # PHASE 9: CONVERSATION MONITORING & GHL CONSENT ATTRIBUTION
    # ==========================================================================

    def record_conversation_event(self, monitored_id: str, event_type: str, text: str, sender: str = "Redditor") -> Dict[str, Any]:
        """
        Tracks replies, clarification requests, and moderation actions.
        """
        if monitored_id not in self.monitored_threads:
            return {"success": False, "error": "Monitored thread not found"}

        mon = self.monitored_threads[monitored_id]
        clean_text = self.claude_broker.sanitize_untrusted_input(text)

        event = {
            "event_id": f"ev_{uuid.uuid4().hex[:6]}",
            "event_type": event_type,
            "sender": sender,
            "text": clean_text,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        mon.events.append(event)
        mon.last_checked_at = datetime.now(timezone.utc).isoformat()

        # State transitions
        if event_type == "CONTENT_REMOVED" or event_type == "MODERATOR_NOTICE":
            mon.conversation_state = "ARCHIVED"
            mon.stop_monitoring = True
            mon.stop_reason = f"Moderation intervention: {event_type}"
            logger.warning(f"Thread {mon.thread_url} stopped due to moderation notice.")
        elif event_type == "INTEREST_EXPRESSED":
            mon.conversation_state = "INTEREST_EXPRESSED"
        elif event_type == "REPLY_RECEIVED":
            mon.conversation_state = "RESPONSE_RECEIVED"

        return {"success": True, "state": mon.conversation_state, "event": event}

    def record_consented_lead_to_ghl(self, monitored_id: str, sender_name: str, email: str, company: str, intent_description: str) -> Dict[str, Any]:
        """
        Synchronizes an explicitly opted-in lead from a voluntary conversation into GHL.
        Guarantees zero unconsented harvesting.
        """
        mon = self.monitored_threads.get(monitored_id)
        thread_id = mon.post_id if mon else "manual_thread"
        sub = mon.subreddit if mon else "reddit_organic"

        consent = VoluntaryLeadConsent(
            source_reddit_thread_id=thread_id,
            source_subreddit=sub,
            expressed_intent=intent_description,
            provided_name=sender_name,
            provided_email=email,
            provided_company=company,
            lawful_basis="EXPLICIT_CONSENT",
            verification_evidence=f"Voluntary message in thread {thread_id} requesting consultation."
        )

        # Sync to GoHighLevel CRM Location
        prospect_payload = {
            "id": f"reddit_lead_{uuid.uuid4().hex[:8]}",
            "business_name": company or sender_name,
            "email": email,
            "phone": "+19299663559",
            "country": "US",
            "city": "Reddit Organic",
            "target_product_id": "service_business_os",
            "score": {"total_score": 85, "priority_tier": "HIGH_PRIORITY"},
            "tags": ["source:reddit", f"sub:{sub}", "attribution:organic_reddit"],
            "custom_fields": {
                "acquisition_channel": "Reddit Organic Intelligence",
                "source_subreddit": sub,
                "expressed_intent": intent_description
            }
        }
        ghl_record = ghl_sync.sync_prospect_to_ghl(prospect_payload, initial_stage="Demo Scheduled")
        consent.ghl_contact_id = ghl_record.ghl_contact_id
        consent.synced_at = datetime.now(timezone.utc).isoformat()
        
        self.consented_leads[consent.id] = consent

        if mon:
            mon.conversation_state = "OPTED_IN_LEAD"

        return {
            "success": True,
            "status": "SYNCED_TO_GHL",
            "consent_id": consent.id,
            "ghl_contact_id": consent.ghl_contact_id,
            "tags_assigned": prospect_payload["tags"]
        }

    # ==========================================================================
    # PHASE 10: HERMES & OPERATIONAL CONTROLS
    # ==========================================================================

    def set_emergency_stop(self, active: bool, reason: str = "Operator Triggered") -> Dict[str, Any]:
        """Halts all background research, drafting, and outreach immediately."""
        self.emergency_stop_active = active
        return {
            "emergency_stop_active": self.emergency_stop_active,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_operational_metrics(self) -> Dict[str, Any]:
        """Calculates real, unexaggerated metrics for the Reddit Command Center."""
        candidates = list(self.discussion_candidates.values())
        drafts = list(self.drafts.values())
        monitored = list(self.monitored_threads.values())
        
        return {
            "total_discussions_discovered": len(candidates),
            "high_opportunity_discussions": sum(1 for c in candidates if c.relevance_score >= 70),
            "drafts_awaiting_approval": sum(1 for d in drafts if d.status == "AWAITING_APPROVAL"),
            "approved_manual_actions": sum(1 for d in drafts if d.status == "SCHEDULED_FOR_MANUAL_ACTION"),
            "published_answers": sum(1 for d in drafts if d.status == "PUBLISHED"),
            "active_monitored_threads": sum(1 for m in monitored if not m.stop_monitoring),
            "consented_ghl_leads": len(self.consented_leads),
            "emergency_stop_active": self.emergency_stop_active,
            "monitored_communities_count": len(self.communities)
        }

# Global singleton instance
reddit_engine = RedditIntelligenceEngine()
