# Alpha Vision — GoHighLevel CRM WhatsApp Integration Architecture
**CRM Location:** `n4sb0M0P3oQhIux2e1Um` ("Alpha Vision")  
**Private Integration Token:** `pit-us-16b618da-...`  
**API Engine:** LeadConnector API v2  

---

## 1. CRM Field Synchronization Registry

The following custom fields have been provisioned directly in GoHighLevel to track WhatsApp communication state without creating competing databases:

| Field Name | GHL Field ID | Model | Type | Purpose |
|---|---|---|---|---|
| **AVM WhatsApp Window Expiry** | `ZG4CF1R3JMBooz9vAz6R` | Contact | TEXT | ISO timestamp when the 24-hour customer service window expires. |
| **AVM WhatsApp Last Message ID** | `0x5nGLlXI6VRRoblU3my` | Contact | TEXT | Meta provider Message ID (`wamid.HBgL...`) of the latest message. |
| **AVM WhatsApp Conversation State** | `k0C3j0lxNj8cVdoFfvmg` | Contact | TEXT | State indicator: `WINDOW_ACTIVE`, `HUMAN_TAKEOVER`, `OPTED_OUT`, `EXPIRED`. |
| **AVM SMS/WhatsApp Consent Evidence** | `XhgrU1U4iWY5M6cWrRic` | Contact | TEXT | Timestamp and source of customer opt-in consent. |

---

## 2. Inbound Contact Lifecycle
When a customer sends a message to the Alpha Vision WhatsApp number:
1. **Webhook Reception:** Meta forwards the message event to `/api/whatsapp/webhook`.
2. **Phone Normalization:** The phone number is converted to clean E.164 format.
3. **Contact Matching:** `whatsapp_ghl_sync.match_or_create_contact` searches GHL for an existing contact with this phone.
   - If found: Contact is matched and updated.
   - If not found: New contact is created with tag `avm_whatsapp_lead`.
4. **Window Extension:** `AVM WhatsApp Window Expiry` is set to `now + 24 hours`.
5. **Conversation Logging:** A note is logged on the contact with message text, time, and Meta message ID.
6. **Takeover Check:** If the customer asks for a human ("quiero hablar con un humano"), the contact is tagged with `avm_human_takeover` and AI responses are locked.

---

## 3. Two-Way GHL Conversation Provider Evaluation (Section 8.3)

### Current GHL Architecture Findings:
- GoHighLevel's official **Custom Conversation Provider** module requires an agency-level Marketplace App with OAuth 2.0 authorization and a registered message provider schema (`POST /conversations/providers`).
- Sub-account Private Integration Tokens (`pit-...`) do not currently have the scope to register global conversation providers across the agency.
- **Recommended & Implemented Path:**
  - HighLevel continues as the authoritative system of record for Contacts, Pipelines, Opportunities, and Appointments.
  - WhatsApp messages are synced as Contact Activity Notes and Custom Field States in GHL.
  - Team members can view real-time WhatsApp conversation history and trigger outbound templates or messages directly from the **WhatsApp Integration Center** (`/whatsapp`) without paying GHL's native recurring WhatsApp add-on fees.
  - This avoids duplicate message sending and guarantees 100% compliance with Meta's 24-hour service window.
