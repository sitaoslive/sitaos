-- ==============================================================================
-- ALPHA VISION REVENUE OS - ADVANCED REDDIT INTELLIGENCE & ENGAGEMENT SCHEMA
-- Migration: 007_reddit_intelligence_schema.sql
-- Description: Creates persistent relational tables for Reddit discovery, community
-- intelligence, opportunity scoring, AI answer drafting, human approval queue,
-- conversation monitoring, voluntary lead consent, and GHL attribution.
-- ==============================================================================

-- 1. Reddit Connections & App Configuration
CREATE TABLE IF NOT EXISTS public.reddit_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL DEFAULT 'alpha_vision_main',
    app_client_id TEXT NOT NULL,
    connection_mode TEXT NOT NULL DEFAULT 'ASSISTED_MANUAL', -- 'ENTERPRISE_API' or 'ASSISTED_MANUAL'
    developer_platform_status TEXT NOT NULL DEFAULT 'PENDING_COMMERCIAL_REVIEW', -- 'APPROVED', 'PENDING_COMMERCIAL_REVIEW', 'OFFLINE'
    rate_limit_remaining INT DEFAULT 100,
    rate_limit_reset_epoch BIGINT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 2. Subreddit Communities
CREATE TABLE IF NOT EXISTS public.reddit_communities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subreddit_name TEXT NOT NULL UNIQUE, -- E.g. 'smallbusiness', 'Entrepreneur', 'HVAC'
    display_title TEXT,
    description TEXT,
    subscriber_count INT DEFAULT 0,
    eligibility_status TEXT NOT NULL DEFAULT 'RESEARCH_ONLY', -- 'APPROVED_FOR_REVIEWED_PARTICIPATION', 'REQUIRES_MODERATOR_CLARIFICATION', 'RESEARCH_ONLY', 'DO_NOT_PARTICIPATE'
    promo_policy TEXT NOT NULL DEFAULT 'PROHIBITED', -- 'PROHIBITED', 'RESTRICTED_MEGA_THREAD', 'ALLOWED_WITH_DISCLOSURE', 'UNKNOWN'
    link_policy TEXT NOT NULL DEFAULT 'NO_LINKS', -- 'NO_LINKS', 'NO_SHORTENERS', 'ALLOWED_RELEVANT'
    flair_required BOOLEAN DEFAULT FALSE,
    preferred_tone TEXT DEFAULT 'EDUCATIONAL_PEER',
    verified_at TIMESTAMPTZ,
    evidence_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 3. Subreddit Community Rules
CREATE TABLE IF NOT EXISTS public.reddit_community_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    community_id UUID NOT NULL REFERENCES public.reddit_communities(id) ON DELETE CASCADE,
    rule_number INT NOT NULL,
    rule_name TEXT NOT NULL,
    rule_description TEXT,
    is_promotion_barrier BOOLEAN NOT NULL DEFAULT FALSE,
    enforcement_priority TEXT DEFAULT 'STRICT',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 4. Research Queries & Search Topics
CREATE TABLE IF NOT EXISTS public.reddit_research_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_cluster TEXT NOT NULL, -- E.g. 'Customer Acquisition', 'Sales Process Problems', 'Disorganized Operations'
    search_phrase TEXT NOT NULL,
    exact_match BOOLEAN NOT NULL DEFAULT FALSE,
    excluded_keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    target_subreddits TEXT[] DEFAULT ARRAY[]::TEXT[],
    language TEXT NOT NULL DEFAULT 'en',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_executed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 5. Discovered Discussion Candidates
CREATE TABLE IF NOT EXISTS public.reddit_discussion_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reddit_post_id TEXT NOT NULL UNIQUE, -- E.g. 't3_1h8a9bc'
    subreddit TEXT NOT NULL,
    title TEXT NOT NULL,
    excerpt TEXT,
    post_url TEXT NOT NULL,
    author_pseudonym TEXT, -- Stored without personally identifiable profiles
    upvotes INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    created_utc TIMESTAMPTZ NOT NULL,
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    relevance_score INT DEFAULT 0, -- 0 to 100
    opportunity_classification TEXT DEFAULT 'MARKET_RESEARCH_ONLY',
    data_access_source TEXT DEFAULT 'AUTHORIZED_QUERY', -- 'AUTHORIZED_QUERY', 'OPERATOR_URL_INPUT', 'DEVVIT_INGEST'
    retention_status TEXT NOT NULL DEFAULT 'ACTIVE' -- 'ACTIVE', 'FLAGGED_FOR_DELETION', 'EXPIRED'
);

-- 6. Opportunity Scores & Analysis
CREATE TABLE IF NOT EXISTS public.reddit_opportunity_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES public.reddit_discussion_candidates(id) ON DELETE CASCADE,
    overall_score INT NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    question_relevance_pts INT DEFAULT 0,
    expertise_match_pts INT DEFAULT 0,
    knowledge_gap_pts INT DEFAULT 0,
    freshness_pts INT DEFAULT 0,
    promotional_risk_penalty INT DEFAULT 0,
    community_multiplier NUMERIC(3,2) DEFAULT 1.0,
    rationale TEXT NOT NULL,
    suggested_action TEXT NOT NULL, -- 'DRAFT_ANSWER', 'MONITOR', 'PASS', 'CREATE_CONTENT_INSPIRATION'
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 7. Content Drafts (Answers & Original Educational Posts)
CREATE TABLE IF NOT EXISTS public.reddit_content_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES public.reddit_discussion_candidates(id) ON DELETE SET NULL,
    content_type TEXT NOT NULL, -- 'SHORT_ANSWER', 'DETAILED_ANSWER', 'STEP_BY_STEP', 'EXPERT_PERSPECTIVE', 'ORIGINAL_POST'
    target_subreddit TEXT NOT NULL,
    draft_title TEXT,
    draft_body TEXT NOT NULL,
    key_takeaway TEXT,
    citations_used TEXT[] DEFAULT ARRAY[]::TEXT[],
    commercial_disclosure TEXT, -- Mandatory disclosure text if business affiliation applies
    status TEXT NOT NULL DEFAULT 'DRAFT', -- 'DRAFT', 'RULES_REVIEW', 'AWAITING_APPROVAL', 'APPROVED', 'REJECTED', 'SCHEDULED_FOR_MANUAL_ACTION', 'PUBLISHED'
    rejection_reason TEXT,
    created_by_agent TEXT DEFAULT 'Reddit Response Architect',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 8. Editorial Reviews & Human Approvals
CREATE TABLE IF NOT EXISTS public.reddit_editorial_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES public.reddit_content_drafts(id) ON DELETE CASCADE,
    reviewed_by TEXT NOT NULL, -- E.g. 'Founder / Platform Owner'
    action_taken TEXT NOT NULL, -- 'APPROVE', 'EDIT_AND_APPROVE', 'REJECT'
    review_notes TEXT,
    rule_checklist_verified BOOLEAN NOT NULL DEFAULT FALSE,
    disclosure_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 9. Publication Results & Tracking
CREATE TABLE IF NOT EXISTS public.reddit_publication_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES public.reddit_content_drafts(id) ON DELETE CASCADE,
    publishing_method TEXT NOT NULL, -- 'MANUAL_OPERATOR_ACTION', 'AUTHORIZED_API'
    reddit_comment_id TEXT, -- E.g. 't1_abc123'
    reddit_permalink TEXT,
    published_by TEXT NOT NULL,
    published_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    status TEXT NOT NULL DEFAULT 'ACTIVE', -- 'ACTIVE', 'REMOVED_BY_MOD', 'DELETED_BY_USER'
    last_verified_at TIMESTAMPTZ
);

-- 10. Monitored Threads & Ongoing Conversations
CREATE TABLE IF NOT EXISTS public.reddit_monitored_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id TEXT NOT NULL UNIQUE,
    subreddit TEXT NOT NULL,
    thread_url TEXT NOT NULL,
    conversation_state TEXT NOT NULL DEFAULT 'POSTED', -- 'POSTED', 'AWAITING_RESPONSE', 'RESPONSE_RECEIVED', 'FOLLOW_UP_DRAFTED', 'CONVERSATION_COMPLETED', 'INTEREST_EXPRESSED', 'OPTED_IN_LEAD'
    last_checked_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    next_check_due TIMESTAMPTZ,
    stop_monitoring BOOLEAN NOT NULL DEFAULT FALSE,
    stop_reason TEXT
);

-- 11. Conversation Events & Inbound Replies
CREATE TABLE IF NOT EXISTS public.reddit_conversation_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    monitored_thread_id UUID NOT NULL REFERENCES public.reddit_monitored_threads(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL, -- 'REPLY_RECEIVED', 'QUESTION_ASKED', 'MODERATOR_NOTICE', 'CONTENT_REMOVED'
    sender_pseudonym TEXT,
    event_snippet TEXT,
    requires_attention BOOLEAN NOT NULL DEFAULT TRUE,
    suggested_followup_id UUID REFERENCES public.reddit_content_drafts(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 12. Voluntary Lead Consents (Strictly Consented Inquiries Only)
CREATE TABLE IF NOT EXISTS public.reddit_lead_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_reddit_thread_id TEXT NOT NULL,
    source_subreddit TEXT NOT NULL,
    expressed_intent TEXT NOT NULL, -- 'EXPLICIT_COMMERCIAL_INTEREST', 'REQUESTED_WEBSITE', 'BOOKED_CALL'
    provided_name TEXT,
    provided_email TEXT,
    provided_company TEXT,
    lawful_basis TEXT NOT NULL DEFAULT 'EXPLICIT_CONSENT',
    consent_timestamp TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    verification_evidence TEXT NOT NULL
);

-- 13. GoHighLevel Mappings
CREATE TABLE IF NOT EXISTS public.reddit_ghl_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consent_id UUID NOT NULL REFERENCES public.reddit_lead_consents(id) ON DELETE CASCADE,
    ghl_location_id TEXT NOT NULL,
    ghl_contact_id TEXT NOT NULL,
    ghl_opportunity_id TEXT,
    ghl_pipeline_stage TEXT DEFAULT 'lead_intake_new',
    attribution_tag TEXT DEFAULT 'source:reddit',
    synced_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 14. Agent Execution & Operational Audit Log
CREATE TABLE IF NOT EXISTS public.reddit_agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    task_name TEXT NOT NULL,
    input_summary TEXT,
    output_summary TEXT,
    tokens_input INT DEFAULT 0,
    tokens_output INT DEFAULT 0,
    cost_usd NUMERIC(8,5) DEFAULT 0.0,
    latency_ms INT DEFAULT 0,
    confidence_score NUMERIC(4,3) DEFAULT 1.0,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Create essential lookup indexes
CREATE INDEX IF NOT EXISTS idx_reddit_communities_name ON public.reddit_communities(subreddit_name);
CREATE INDEX IF NOT EXISTS idx_reddit_candidates_score ON public.reddit_discussion_candidates(relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_reddit_drafts_status ON public.reddit_content_drafts(status);
CREATE INDEX IF NOT EXISTS idx_reddit_monitored_state ON public.reddit_monitored_threads(conversation_state);
CREATE INDEX IF NOT EXISTS idx_reddit_ghl_contact ON public.reddit_ghl_mappings(ghl_contact_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.reddit_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reddit_communities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reddit_community_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reddit_research_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reddit_discussion_candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reddit_opportunity_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reddit_content_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reddit_editorial_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reddit_publication_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reddit_monitored_threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reddit_conversation_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reddit_lead_consents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reddit_ghl_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reddit_agent_runs ENABLE ROW LEVEL SECURITY;
