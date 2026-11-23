"""
Alpha Vision Revenue OS - WhatsApp Cost Control & Budgeting Engine
Calculates official Meta Cloud API conversation charges, tracks monthly & daily expenditure,
and automatically enforces emergency spending pauses before budget overruns.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("whatsapp_cost")
logger.setLevel(logging.INFO)

# Official Meta Cloud API Standard Regional Rates (Per Conversation / Delivery Window)
# References: Meta Business Platform Conversation-Based Pricing
META_RATES_USD = {
    "US": {
        "marketing": 0.0250,
        "utility": 0.0150,
        "authentication": 0.0135,
        "service": 0.0050
    },
    "CA": {
        "marketing": 0.0250,
        "utility": 0.0150,
        "authentication": 0.0135,
        "service": 0.0050
    },
    "CO": {
        "marketing": 0.0125,
        "utility": 0.0080,
        "authentication": 0.0070,
        "service": 0.0040
    },
    "MX": {
        "marketing": 0.0430,
        "utility": 0.0250,
        "authentication": 0.0200,
        "service": 0.0105
    },
    "GLOBAL_DEFAULT": {
        "marketing": 0.0350,
        "utility": 0.0200,
        "authentication": 0.0150,
        "service": 0.0080
    }
}

class WhatsAppCostController:
    """Manages real-time cost telemetry, budget safety limits, and billing ledger."""

    def __init__(self, monthly_budget_usd: float = 150.0, daily_budget_usd: float = 15.0):
        self.monthly_budget_usd = monthly_budget_usd
        self.daily_budget_usd = daily_budget_usd
        
        # Telemetry counters
        self.total_messages_sent: int = 0
        self.total_messages_delivered: int = 0
        self.total_messages_failed: int = 0
        self.total_cost_usd: float = 0.0
        self.daily_cost_usd: float = 0.0
        self.free_tier_conversations_used: int = 0
        self.current_month: str = datetime.now(timezone.utc).strftime("%Y-%m")
        self.current_day: str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _refresh_period(self):
        now_month = datetime.now(timezone.utc).strftime("%Y-%m")
        now_day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if now_month != self.current_month:
            logger.info(f"Resetting monthly WhatsApp budget ledger for {now_month}")
            self.total_cost_usd = 0.0
            self.free_tier_conversations_used = 0
            self.current_month = now_month
        if now_day != self.current_day:
            self.daily_cost_usd = 0.0
            self.current_day = now_day

    def infer_country(self, phone: str) -> str:
        """Infers country code from E.164 phone prefix."""
        clean = "".join(filter(str.isdigit, str(phone)))
        if clean.startswith("57"):
            return "CO"
        elif clean.startswith("52"):
            return "MX"
        elif clean.startswith("1"):
            return "US"
        return "GLOBAL_DEFAULT"

    def estimate_message_cost(self, phone: str, category: str = "service") -> float:
        """Returns the estimated Meta fee in USD for a given message category and destination."""
        self._refresh_period()
        country = self.infer_country(phone)
        rate_table = META_RATES_USD.get(country, META_RATES_USD["GLOBAL_DEFAULT"])
        rate = rate_table.get(category.lower(), rate_table["service"])

        # First 1,000 Service conversations per WABA per month are 100% free under Meta policy
        if category.lower() == "service" and self.free_tier_conversations_used < 1000:
            return 0.0000

        return rate

    def can_send_outbound(self, estimated_cost: float = 0.025) -> Tuple[bool, Optional[str]]:
        """Verifies whether the monthly and daily budget caps allow new outbound dispatch."""
        self._refresh_period()
        if (self.total_cost_usd + estimated_cost) > self.monthly_budget_usd:
            return False, f"Monthly budget limit of ${self.monthly_budget_usd:.2f} reached. Outbound paused."
        if (self.daily_cost_usd + estimated_cost) > self.daily_budget_usd:
            return False, f"Daily budget limit of ${self.daily_budget_usd:.2f} reached. Outbound paused for today."
        return True, None

    def record_message_event(self, phone: str, category: str, status: str = "sent"):
        """Records telemetry and billable cost for a processed message."""
        self._refresh_period()
        cost = self.estimate_message_cost(phone, category)

        if category.lower() == "service" and self.free_tier_conversations_used < 1000:
            self.free_tier_conversations_used += 1

        self.total_messages_sent += 1
        if status == "delivered":
            self.total_messages_delivered += 1
        elif status == "failed":
            self.total_messages_failed += 1

        self.total_cost_usd += cost
        self.daily_cost_usd += cost

        logger.info(f"Recorded WA cost: +${cost:.4f} USD | Total MTD: ${self.total_cost_usd:.4f} | Free Tier: {self.free_tier_conversations_used}/1000")

    def get_summary(self) -> Dict[str, Any]:
        """Provides an authoritative dashboard summary for the WhatsApp Integration Center."""
        self._refresh_period()
        return {
            "monthly_budget_usd": self.monthly_budget_usd,
            "daily_budget_usd": self.daily_budget_usd,
            "total_cost_mtd_usd": round(self.total_cost_usd, 4),
            "daily_cost_usd": round(self.daily_cost_usd, 4),
            "monthly_remaining_usd": round(max(0.0, self.monthly_budget_usd - self.total_cost_usd), 4),
            "messages_sent": self.total_messages_sent,
            "messages_delivered": self.total_messages_delivered,
            "messages_failed": self.total_messages_failed,
            "free_tier_conversations_used": self.free_tier_conversations_used,
            "free_tier_remaining": max(0, 1000 - self.free_tier_conversations_used),
            "budget_alert_active": (self.total_cost_usd / self.monthly_budget_usd) >= 0.85
        }

whatsapp_cost = WhatsAppCostController()
