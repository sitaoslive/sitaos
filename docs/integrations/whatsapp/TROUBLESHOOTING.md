# Alpha Vision — WhatsApp Integration Troubleshooting Guide

---

## 1. Common Errors & Resolution Steps

### Error 1: "SERVICE_WINDOW_EXPIRED"
- **Symptom:** Outbound message attempt returns:
  `"Meta policy forbids free-form text messages outside the 24-hour customer window."`
- **Cause:** More than 24 hours have elapsed since the customer last sent a message to the business WhatsApp number.
- **Resolution:** You cannot send arbitrary free-form text. You must select an **Approved Meta Template** (e.g. `avm_onboarding_reminder_v1`) to re-open the conversation.

---

### Error 2: "CONTACT_SUPPRESSED"
- **Symptom:** Outbound message attempt returns:
  `"Contact has opted out (STOP / PARAR). Sending is strictly prohibited."`
- **Cause:** The contact previously sent an opt-out keyword (`STOP`, `PARAR`, `CANCELAR`, `BAJA`).
- **Resolution:** By law and Meta platform policy, proactive messaging cannot be sent to an opted-out contact. The contact must initiate a new conversation or explicitly request re-subscription.

---

### Error 3: Meta Webhook Verification Fails (HTTP 403)
- **Symptom:** When clicking "Verify and Save" in Meta Developer Console, an error occurs.
- **Cause:** Verify Token mismatch or server unreachable.
- **Resolution:**
  1. Confirm your public endpoint URL ends with `/api/whatsapp/webhook`.
  2. Confirm Verify Token is exactly: `alpha_vision_meta_wa_2026_webhook_verify`.
  3. Verify the server is running (`python server.py`).

---

### Error 4: "QUIET_HOURS_VIOLATION"
- **Symptom:** Outbound message blocked between 8:00 PM and 8:00 AM local time.
- **Cause:** TCPA / campaign safety guardrail preventing non-emergency outbound messaging during quiet hours.
- **Resolution:** The message will be queued and eligible for dispatch when quiet hours end at 8:00 AM.
