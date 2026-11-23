# Alpha Vision — WhatsApp Cost Control & Budget Architecture
**Budget Objective:** Eliminate third-party SaaS subscription fees while enforcing strict budget guardrails on official Meta usage charges.

---

## 1. Meta Official Conversation Rates (Per 24h Window)

Meta does not charge per individual message. Instead, charges are based on **24-hour conversation sessions** categorized into four types:

| Market | Service (User-Initiated) | Utility (Templates) | Marketing (Templates) | Authentication |
|---|---|---|---|---|
| **United States (US)** | **FREE** (1st 1,000/mo) → $0.0050 | $0.0150 | $0.0250 | $0.0135 |
| **Canada (CA)** | **FREE** (1st 1,000/mo) → $0.0050 | $0.0150 | $0.0250 | $0.0135 |
| **Colombia (CO)** | **FREE** (1st 1,000/mo) → $0.0040 | $0.0080 | $0.0125 | $0.0070 |
| **Mexico (MX)** | **FREE** (1st 1,000/mo) → $0.0105 | $0.0250 | $0.0430 | $0.0200 |

> [!NOTE]
> Every WhatsApp Business Account receives **1,000 free service (customer-initiated) conversations each calendar month**.

---

## 2. Hard Budget Limits & Automatic Spending Pauses

The system enforces two strict automated thresholds in `engine/whatsapp_cost.py`:

```python
monthly_budget_usd = 150.00  # Hard monthly ceiling
daily_budget_usd   = 15.00   # Hard daily throttle
```

### Protection Mechanics:
1. **Pre-Flight Check:** Before any message or template is dispatched, `can_send_outbound()` calculates whether the estimated charge would exceed the daily or monthly limit.
2. **Emergency Pause:** If either threshold is reached:
   - Proactive outbound sending is automatically blocked.
   - An alert is flagged in the WhatsApp Integration Center.
   - Customer-initiated service replies within the free tier continue uninterrupted.
3. **Monthly Reset:** On the first day of each calendar month, the MTD ledger resets automatically.

---

## 3. Comparison: Direct Meta vs. Third-Party Connectors

| Expense Item | Third-Party Connector (Wati, Twilio, etc.) | Direct Meta Cloud API (Alpha Vision) |
|---|---|---|
| **Platform Subscription** | $49 to $199 / month | **$0 / month** |
| **Per-User Seat Fee** | $15 to $35 / seat / month | **$0 / month** |
| **Message Markup** | 20% to 50% above Meta rates | **Zero markup** (Official Meta base rates) |
| **Free Tier Access** | Often kept by the provider | **100% of 1,000 free chats credited to you** |
| **Annual Savings** | — | **$1,200 to $3,500 / year** |
