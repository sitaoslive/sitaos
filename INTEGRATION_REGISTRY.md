# ALPHA VISION AUTONOMOUS REVENUE OS — INTEGRATION REGISTRY
**Security Notice:** Zero raw secrets or private keys are stored in this registry or committed to Git. Only safe external asset IDs, endpoints, and verification states are documented.

---

## 1. CONNECTED SERVICES REGISTRY

| Provider | Service Function | Base Endpoint / Resource | Verified External Asset ID | Verification Status |
|---|---|---|---|---|
| **GoHighLevel (LeadConnector v2)** | Sales CRM, Pipelines, Calendars, Contacts | `https://services.leadconnectorhq.com` | Location: `n4sb0M0P3oQhIux2e1Um` | **VERIFIED LIVE (HTTP 200)** |
| **Meta WhatsApp Business Platform** | Official WhatsApp Cloud API (Graph v21.0) | `https://graph.facebook.com/v21.0` | Phone ID: `773036932566233`<br>WABA ID: `766675155993028`<br>App ID: `790054260646946` | **VERIFIED LIVE (HTTP 200)** |
| **Meta Approved Templates** | Onboarding Reminder (Utility) | Graph API Template Endpoint | Template ID: `2250603712470808` | **REGISTERED (HTTP 200)** |
| **n8n Cloud** | Workflow Orchestration Bus | `https://alphavision.app.n8n.cloud` | Project: `DoPm60I3EipMm6rG`<br>Folder: `UZBaq5mx4HuFbm8n` | **VERIFIED LIVE (HTTP 200)** |
| **Supabase (PostgreSQL)** | Application Database, Ledger, Consents | `https://djtejmrzxfkctbvpdkbg.supabase.co` | Project Ref: `djtejmrzxfkctbvpdkbg` | **VERIFIED LIVE (HTTP 200)** |
| **Claude API (Anthropic)** | Cognitive Reasoning & Synthesis | `https://api.anthropic.com/v1/messages` | Models: `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022` | **CONFIGURED & TESTED** |
| **Stripe Payments** | US / International Checkout & Subscriptions | `https://api.stripe.com/v1` | Webhook Receiver: `/api/v1/billing/webhook/stripe` | **STAGING TESTED** |
| **Wompi Payments** | Colombia Local Checkout & Subscriptions | `https://production.wompi.co/v1` | Webhook Receiver: `/api/v1/billing/webhook/wompi` | **STAGING TESTED** |

---

## 2. SYSTEM CAPABILITY MATRIX

| Capability | Execution Owner | Secondary Adapter | Autonomy Level |
|---|---|---|---|
| Inbound Lead Capture | n8n / FastAPI Webhook | GHL Contacts API | A4 (Autonomous) |
| WhatsApp Message Dispatch | Meta Graph API Client | n8n Dispatcher | A4 (Autonomous) |
| 24h Window & TCPA Policy | Deterministic Policy Broker | Supabase `contact_consents` | A4 (Autonomous) |
| Inbound Reply Processing | Webhook Processor + Claude | GHL Conversation Notes | A3 (Autonomous within Policy) |
| Appointment Booking | GHL Calendars API v2 | Supabase `appointments` | A4 (Autonomous) |
| Human Escalation Lock | Tagging Gate | GHL Tag `avm_human_takeover` | A4 (Autonomous) |
| Financial Ledger Reconciliation | Financial Ledger Engine | Supabase `financial_ledger` | A4 (Autonomous) |
| Post-Purchase 1-on-1 Onboarding | Human Specialist | AI Onboarding Briefing (Agent 13) | A2 (Intentional Human Touchpoint) |
