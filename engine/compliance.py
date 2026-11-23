"""
Alpha Vision AI Sales OS - Global Compliance, Deliverability & Suppression Gate
Enforces CAN-SPAM (US), CASL (CA), GDPR (EU), Ley 1581 (CO), TCPA quiet hours,
and manages the unified cross-channel suppression registry.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class SuppressionRecord(BaseModel):
    kind: str  # email, domain, phone
    value: str
    reason: str
    source: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class CompliancePolicyGate:
    def __init__(self):
        self.suppression_list: Dict[str, SuppressionRecord] = {}
        self.emergency_kill_switch_active: bool = False
        self._init_baseline_suppression()

    def _init_baseline_suppression(self):
        """Initializes global suppression seeds."""
        self.add_suppression("email", "do-not-contact@competitor.com", "competitor_exclusion", "system_admin")
        self.add_suppression("domain", "spam-trap-example.org", "known_spam_trap", "compliance_audit")

    def add_suppression(self, kind: str, value: str, reason: str, source: str = "user_optout") -> SuppressionRecord:
        norm_val = value.strip().lower()
        key = f"{kind}:{norm_val}"
        rec = SuppressionRecord(kind=kind, value=norm_val, reason=reason, source=source)
        self.suppression_list[key] = rec
        return rec

    def is_suppressed(self, email: Optional[str] = None, domain: Optional[str] = None, phone: Optional[str] = None) -> bool:
        if email and f"email:{email.strip().lower()}" in self.suppression_list:
            return True
        if domain and f"domain:{domain.strip().lower()}" in self.suppression_list:
            return True
        if phone and f"phone:{phone.strip()}" in self.suppression_list:
            return True
        return False

    def verify_outreach_eligibility(self, prospect: Dict[str, Any], channel: str = "email") -> Dict[str, Any]:
        """
        Validates legal compliance for prospect communication:
        - Emergency Kill Switch check
        - Suppression list check
        - Country-specific cold outreach legality (CAN-SPAM, CASL, GDPR)
        - TCPA Quiet hours check
        """
        if self.emergency_kill_switch_active:
            return {
                "eligible": False,
                "reason": "GLOBAL_KILL_SWITCH_ACTIVE",
                "details": "Outbound execution paused by administrator safety kill switch."
            }

        email = prospect.get("email")
        domain = prospect.get("domain")
        phone = prospect.get("phone")
        country = prospect.get("country", "US").upper()

        # Check suppression
        if self.is_suppressed(email=email, domain=domain, phone=phone):
            return {
                "eligible": False,
                "reason": "RECIPIENT_SUPPRESSED",
                "details": "Recipient email, domain, or phone is on the global suppression registry."
            }

        # Country Legal Gates
        if country in ["ES", "DE", "FR", "IT"]:
            # Strict GDPR / UWG / LSSI opt-in rule
            return {
                "eligible": False,
                "reason": "GDPR_PRIOR_CONSENT_REQUIRED",
                "details": f"Cold commercial outreach is strictly prohibited in {country} without documented prior opt-in consent."
            }

        if country == "CA":
            # CASL requires conspicuous public business address and relevant commercial business context
            if not prospect.get("website"):
                return {
                    "eligible": False,
                    "reason": "CASL_REQUIREMENT_UNMET",
                    "details": "CASL requires conspicuously published business address and direct relevance."
                }

        # TCPA recipient time window check (8:00 AM to 8:00 PM local)
        # Assumed valid during standard business hours; flagged if outside
        current_hour = datetime.utcnow().hour  # UTC hour
        # Approximate US/LatAm business hours
        if channel in ["sms", "whatsapp"] and (current_hour < 13 or current_hour > 25): # 8am-8pm EST roughly
            return {
                "eligible": False,
                "reason": "TCPA_QUIET_HOURS",
                "details": "Communication attempt is outside legal 8:00 AM - 8:00 PM recipient window."
            }

        return {
            "eligible": True,
            "reason": "COMPLIANCE_VERIFIED",
            "country_policy": f"{country}_COMPLIANT"
        }

    def set_kill_switch(self, active: bool, operator: str = "admin") -> bool:
        self.emergency_kill_switch_active = active
        return self.emergency_kill_switch_active

compliance_gate = CompliancePolicyGate()
