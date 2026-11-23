# ALPHA VISION AUTONOMOUS REVENUE OS — DECISION REGISTER
**Format:** ADR (Architecture Decision Record)  
**Maintained by:** Principal Systems Architect  

---

## ADR-001: Google Antigravity as Sole Development Environment
- **Context:** Project requires complex agent orchestration, multi-service testing, and live API connectivity.
- **Decision:** All code, tests, schemas, and configurations are developed and verified inside Google Antigravity. External services (Supabase, GHL, n8n Cloud, Meta) are production runtimes, not coding environments.
- **Status:** APPROVED & ENFORCED.

---

## ADR-002: Managed Configurable SaaS Templates over Bespoke Code
- **Context:** Individual custom consulting code cannot scale automatically to 150+ customers.
- **Decision:** Standardize tested industry templates (HVAC/Contractor and Mobile Vet) and configure business facts (hours, pricing rules, services, calendars) via structured tenant parameters rather than deploying custom codebases per client.
- **Status:** APPROVED & ENFORCED.

---

## ADR-003: Deterministic Policy Enforcement over Unconstrained LLM Actions
- **Context:** AI models can hallucinate prices, commit to unauthorized discounts, or send messages outside TCPA quiet hours.
- **Decision:** Claude API generates drafts, reasons over unstructured data, and proposes structured actions. A deterministic software broker validates permissions, budgets, suppression lists, prices, and 24h service windows before any external dispatch.
- **Status:** APPROVED & ENFORCED.

---

## ADR-004: Direct Official Meta WhatsApp Cloud API over Third-Party Connectors
- **Context:** Third-party WhatsApp wrappers charge $49–$199/mo plus markup, and web-scraping bots risk business number bans.
- **Decision:** Connect directly to Meta WhatsApp Cloud API (Graph API v21.0) using permanent System User tokens, utilizing the 1,000 monthly free tier service chats and paying official regional rates with zero middleware markup.
- **Status:** APPROVED & IMPLEMENTED (Phone ID: `773036932566233`, WABA: `766675155993028`).

---

## ADR-005: 1-on-1 Human Onboarding Touchpoint Post-Purchase
- **Context:** Enterprise SaaS retention requires successful configuration of the client's actual calendars and business rules.
- **Decision:** After checkout and automatic tenant provisioning, client schedules a 45–60 minute implementation call via GHL Calendar `bt3iaUkXMR70vdSS9UQo` guided by an automated AI Briefing.
- **Status:** APPROVED & IMPLEMENTED.
