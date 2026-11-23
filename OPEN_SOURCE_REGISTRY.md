# ALPHA VISION AUTONOMOUS REVENUE OS — OPEN-SOURCE EVALUATION REGISTRY
**Objective:** Leverage battle-tested open-source libraries to avoid reinventing infrastructure, while verifying licenses, maintenance, and security.

---

## Evaluated Packages

| Library / Tool | Function | License | Maintenance / Security Status | Decision | Rationale |
|---|---|---|---|---|---|
| **FastAPI** | REST API & Webhook Server | MIT | Actively Maintained, High Performance | **ADOPTED** | Powers Executive Command Center & Webhook Ingress |
| **Pydantic v2** | Data Validation & Schema | MIT | Industry Standard, C-extension speed | **ADOPTED** | Enforces typed schemas across all 35 workflows |
| **Uvicorn** | ASGI Web Server | BSD | Highly Reliable, Async I/O | **ADOPTED** | Lightweight runtime for production API |
| **pytest / pytest-asyncio** | Automated Test Framework | MIT | Standard Python test runner | **ADOPTED** | Powers 54+ unit, integration, and safety tests |
| **Anthropic SDK** | Claude Messages API | MIT | Official Anthropic library | **ADOPTED** | Connects Sonnet & Haiku models with prompt caching |
| **BullMQ / Redis** | Message Queue | MIT | Requires external Redis cluster | **DEFERRED** | Supabase PostgreSQL + in-memory queue selected for simplicity |
| **Temporal.io** | Distributed Workflow Engine | MIT | High operational footprint for initial scale | **DEFERRED** | n8n Cloud + Python sagas fulfill all current requirements |
