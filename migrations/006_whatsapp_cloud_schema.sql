-- ==============================================================================
-- ALPHA VISION REVENUE OS - OFFICIAL META WHATSAPP CLOUD API SCHEMA
-- Migration: 006_whatsapp_cloud_schema.sql
-- Description: Creates dedicated durable tables for WhatsApp Cloud API integration,
-- message events, contact mappings, consent records, templates, and cost tracking.
-- ==============================================================================

-- 1. WhatsApp Connections (Stores WABA, Phone Number ID, Status)
CREATE TABLE IF NOT EXISTS public.whatsapp_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL DEFAULT 'alpha_vision_main',
    waba_id TEXT NOT NULL,
    phone_number_id TEXT NOT NULL UNIQUE,
    display_phone_number TEXT,
    verified_name TEXT,
    quality_rating TEXT DEFAULT 'UNKNOWN',
    status TEXT NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, PENDING_VERIFICATION, SUSPENDED
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 2. WhatsApp Contact Mappings (Maps WhatsApp WA_ID to GHL & Internal Contact ID)
CREATE TABLE IF NOT EXISTS public.whatsapp_contact_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wa_id TEXT NOT NULL UNIQUE, -- E.g., '573154448899' or '17865551234'
    phone_e164 TEXT NOT NULL,
    ghl_contact_id TEXT,
    supabase_contact_id UUID REFERENCES public.contacts(id) ON DELETE SET NULL,
    display_name TEXT,
    preferred_language TEXT DEFAULT 'es',
    last_inbound_at TIMESTAMPTZ,
    last_outbound_at TIMESTAMPTZ,
    service_window_expires_at TIMESTAMPTZ,
    human_takeover_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 3. WhatsApp Messages (Stores Inbound & Outbound WhatsApp Messages with Meta IDs)
CREATE TABLE IF NOT EXISTS public.whatsapp_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meta_message_id TEXT UNIQUE, -- E.g. 'wamid.HBgL...'
    direction TEXT NOT NULL CHECK (direction IN ('INBOUND', 'OUTBOUND')),
    phone_number_id TEXT NOT NULL,
    wa_id TEXT NOT NULL,
    ghl_contact_id TEXT,
    message_type TEXT NOT NULL DEFAULT 'text', -- text, template, image, document, audio, interactive
    body TEXT,
    template_name TEXT,
    delivery_status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, SENT, DELIVERED, READ, FAILED
    error_code TEXT,
    error_message TEXT,
    idempotency_key TEXT UNIQUE,
    cost_estimated_usd NUMERIC(8, 4) DEFAULT 0.0000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 4. WhatsApp Webhook Events (Raw Auditable Ingestion Log)
CREATE TABLE IF NOT EXISTS public.whatsapp_webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id TEXT UNIQUE,
    event_type TEXT NOT NULL, -- message, status, error
    payload JSONB NOT NULL,
    signature_verified BOOLEAN NOT NULL DEFAULT FALSE,
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    processed_at TIMESTAMPTZ,
    error_details TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 5. WhatsApp Templates Registry (Approved Meta Templates)
CREATE TABLE IF NOT EXISTS public.whatsapp_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    waba_id TEXT NOT NULL,
    name TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'es',
    category TEXT NOT NULL CHECK (category IN ('UTILITY', 'MARKETING', 'AUTHENTICATION')),
    status TEXT NOT NULL DEFAULT 'APPROVED', -- APPROVED, REJECTED, PENDING, PAUSED
    components JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    UNIQUE(waba_id, name, language)
);

-- 6. WhatsApp Cost & Usage Ledger
CREATE TABLE IF NOT EXISTS public.whatsapp_cost_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meta_message_id TEXT,
    wa_id TEXT NOT NULL,
    category TEXT NOT NULL, -- utility, marketing, authentication, service
    market_iso TEXT NOT NULL DEFAULT 'US',
    rate_usd NUMERIC(8, 4) NOT NULL DEFAULT 0.0000,
    billed_by_meta BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Indexes for High-Performance Real-Time Webhook Processing
CREATE INDEX IF NOT EXISTS idx_wa_messages_wa_id ON public.whatsapp_messages(wa_id);
CREATE INDEX IF NOT EXISTS idx_wa_messages_meta_id ON public.whatsapp_messages(meta_message_id);
CREATE INDEX IF NOT EXISTS idx_wa_mappings_wa_id ON public.whatsapp_contact_mappings(wa_id);
CREATE INDEX IF NOT EXISTS idx_wa_mappings_ghl_id ON public.whatsapp_contact_mappings(ghl_contact_id);
CREATE INDEX IF NOT EXISTS idx_wa_events_processed ON public.whatsapp_webhook_events(processed);
