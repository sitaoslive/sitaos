# ALPHA VISION AUTONOMOUS REVENUE OS — MASTER SPECIFICATION
**System:** Alpha Vision Autonomous Revenue OS  
**Organization:** Alpha Vision Method (`alphavisionmethod@gmail.com`)  
**Version:** 3.0.0 (Unified Master Build)  
**Reporting Currency:** USD ($) | **Owner Timezone:** America/Bogota  
**Primary Financial Objective:** **$50,000+ USD per month in sustainable recurring net operating profit before tax.**

---

## 1. EXECUTIVE MISSION & CORE COMMERCIAL LOGIC

Alpha Vision Autonomous Revenue OS is the internal acquisition, sales, conversion, delivery, and retention operating system for Alpha Vision Method.

### Core Truths & Architectural Decisions:
1. **Internal Acquisition Engine vs. Customer Products:**  
   This system is Alpha Vision's own operating engine. Customer products (e.g. Service Business OS for contractors, Vet Life / Vet Freedom OS for mobile veterinarians) belong in an approved, versioned offer catalog.
2. **Initial Commercial Beachhead ($499/mo):**  
   Managed Lead-Response and Estimate-Follow-Up Service for small US and Canadian HVAC & Plumbing businesses (2–15 staff). Solves an urgent, measurable financial problem: capturing after-hours missed inquiries and following up on unapproved estimates that owners and technicians lack time to track.
3. **The $50,000/mo Net Operating Profit Target:**  
   Net operating profit is defined strictly as:
   $$\text{Net Operating Profit} = \text{Recurring Recognized Revenue} - (\text{Refunds/Chargebacks} + \text{AI Costs} + \text{Messaging Costs} + \text{Infrastructure} + \text{Payment Fees} + \text{Support Costs} + \text{Shared Overhead})$$
   At $499/month with $99 estimated variable cost per customer and $10,000 shared fixed costs, the target requires **150 retained paying customers** generating $74,850/mo revenue with $24,850/mo total costs.
4. **Division of Responsibility:**  
   - **Claude API:** Deep cognitive reasoning, research synthesis, personalization, and objection drafting.
   - **Deterministic Code:** Permissions, pricing resolution, payment webhooks, calendar booking concurrency, quiet hours, suppression lists, and state transitions.
   - **GoHighLevel (GHL):** Single source of truth for CRM contacts, sales pipeline stages, calendars, and conversation activity.
   - **n8n Cloud:** Integration orchestration bus and webhook connectors.
   - **Supabase PostgreSQL:** Durable multi-tenant application state, event ledger, telemetry, and contact consents.
   - **Meta WhatsApp Cloud API (Graph API v21.0):** Official direct WhatsApp messaging with zero third-party connector fees.
5. **Autonomy Mandate (A4 Target):**  
   Every routine, eligible commercial workflow operates autonomously under preapproved policy bounds. Human involvement is strictly reserved for credentials, missing integrations, legal authorizations, high-risk commitments, and post-purchase 1-on-1 onboarding calls.

---

## 2. PRODUCTION ARCHITECTURE & DATA FLOW

```text
                               ALPHA VISION AUTONOMOUS REVENUE OS
                                                |
                              EXECUTIVE COMMAND CENTER (PORT 8000)
                                                |
                       +------------------------+------------------------+
                       |                                                 |
             CLAUDE REASONING BROKER                          DETERMINISTIC POLICY BROKER
        (Prompt Caching / Token Guardrails)                 (24h Window / Suppression / Pricing)
                       |                                                 |
                       +------------------------+------------------------+
                                                |
                                   AUTONOMOUS REVENUE ORCHESTRATOR
                                     (35 Workflow Families: WF-001 - WF-035)
                                                |
               +----------------+---------------+----------------+----------------+
               |                |               |                |                |
         GOHIGHLEVEL CRM    n8n CLOUD     SUPABASE DB       META WHATSAPP      STRIPE / WOMPI
         (PIT Location)   (Sales OS Bus)  (PostgreSQL)      (Graph API v21)     (Webhooks)
               |                |               |                |                |
               +----------------+---------------+----------------+----------------+
                                                |
                                   PROSPECT & CUSTOMER UNIVERSE
                                (HVAC, Plumbing, Mobile Vets, SaaS)
```

---

## 3. SEVEN CORE COMMERCIAL JOURNEYS

1. **HVAC / Service Contractor Journey:** Discovery → Research → Personalized Estimate Gap Outreach → Inbound Reply → Progressive Qualification → Interactive Mobile Demo → Standard Checkout ($499/mo) → Payment Confirmed → Automatic Provisioning → Specialist Briefing & 1-on-1 Call.
2. **Veterinary Clinic (Vet Life OS) Journey:** Spanish-language discovery in Colombia/Mexico → Clinic Workflow Research → Inbound WhatsApp / Form → Consultation or Self-Serve Checkout → Subscription Provisioning → Staff Training Briefing.
3. **Inbound Organic Acquisition Journey:** Interactive ROI Calculator & Workflow Visualizer → Form Submission → GHL Stage Sync → Automated Follow-Up → Consultation / Checkout.
4. **Self-Service Standard Sale Journey:** Direct checkout on approved plan → Webhook verification → Instant tenant provisioning → Customer portal access.
5. **Human Takeover & AI Pause Journey:** Customer requests human assistance or agent claims chat in GHL → AI auto-replies instantly locked → Staff notification dispatched → Conversation context preserved.
6. **System Recovery & Backpressure Journey:** External API failure or rate limit detected → Exponential backoff & jitter → Dead-letter queue persistence → Automatic reconciliation on recovery.
7. **Subscription Cancellation & Churn Journey:** Cancellation requested → Billing cycle completion scheduled → Survey triggered → Access revoked at period end → Audit records preserved.
