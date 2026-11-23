# ALPHA VISION AUTONOMOUS REVENUE OS — BLOCKERS & DEPENDENCY LEDGER
**Last Audit:** 2026-11-23  
**Status:** All core foundational dependencies CONNECTED & OPERATIONAL.  

---

## 1. ACTIVE LIVE DEPENDENCIES STATUS

| Dependency | Component | Status | Verification Detail | Next Action / Notes |
|---|---|---|---|---|
| **Meta Graph API Token** | WhatsApp Cloud API | **UNBLOCKED (LIVE)** | Permanent System User Token generated for Daniela Wild | Ready for outbound test message |
| **Meta WABA & Phone ID** | WhatsApp Cloud API | **UNBLOCKED (LIVE)** | WABA `766675155993028`, Phone ID `773036932566233` | Live verified via Graph API v21.0 |
| **GHL Private Integration** | Sales CRM API v2 | **UNBLOCKED (LIVE)** | Token `pit-us-16b618da-...` on Location `n4sb0M0P3oQhIux2e1Um` | 4 pipelines, 4 calendars, 3 custom fields verified |
| **n8n Cloud Webhooks** | Workflow Bus | **UNBLOCKED (LIVE)** | Workflows active in folder `UZBaq5mx4HuFbm8n` | HTTP 200 webhooks responding |
| **Supabase PostgreSQL** | Application State | **UNBLOCKED (LIVE)** | REST API `djtejmrzxfkctbvpdkbg` | HTTP 200 inserts verified |
| **Claude API Key** | Cognitive Reasoning | **CONFIGURED** | Key in `.env`, models Sonnet & Haiku | Server-side broker enforcing budget caps |
| **Live Production Outreach** | Campaign Dispatch | **INTENTIONALLY GATED** | Policy Gate `KILL_SWITCH_ACTIVE = False` | Requires final user approval before real cold send |

---

## 2. NON-BLOCKING OPERATIONAL REQUIREMENTS
- **Meta Phone Number Verification:** Display number `+1 929-966-3559` shows `code_verification_status: EXPIRED` in Meta API. When ready to send to non-test external numbers, complete the SMS 2FA code verification in Meta Business Suite if prompted.
