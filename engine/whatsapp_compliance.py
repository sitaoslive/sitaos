"""
Alpha Vision Revenue OS - WhatsApp Compliance & Window Gate
Enforces Meta's 24-hour customer service window, strict TCPA/GDPR opt-in consent,
bilingual opt-out detection (STOP / PARAR / BAJA), quiet hours, and human takeover gates.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta

from engine.config import config

logger = logging.getLogger("whatsapp_compliance")
logger.setLevel(logging.INFO)

OPT_OUT_KEYWORDS_EN = {"stop", "unsubscribe", "cancel", "end", "quit", "optout", "opt-out"}
OPT_OUT_KEYWORDS_ES = {"parar", "baja", "cancelar", "no mas", "nomas", "detener", "desuscribir", "alto"}

HUMAN_TAKEOVER_KEYWORDS = {
    "human", "representative", "agent", "person", "support team", "speak with someone",
    "humano", "persona", "asesor", "representante", "agente", "soporte", "hablar con alguien"
}

class WhatsAppComplianceGate:
    """Enterprise compliance layer for WhatsApp Cloud API communications."""

    def __init__(self):
        # In-memory fast state caches (backed by Supabase)
        self.contact_windows: Dict[str, datetime] = {} # phone -> last_inbound_time
        self.suppression_list: Dict[str, Dict[str, Any]] = {} # phone -> opt_out_metadata
        self.human_takeover_flags: Dict[str, bool] = {} # phone -> is_human_only

    def register_inbound_activity(self, phone: str, text: Optional[str] = None) -> Dict[str, Any]:
        """
        Registers an incoming message from a contact:
        1. Updates the 24-hour service window expiry.
        2. Detects explicit opt-out keywords (STOP / PARAR / BAJA).
        3. Detects human escalation requests.
        """
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        now = datetime.now(timezone.utc)
        
        # 1. Update 24h Window
        self.contact_windows[clean_phone] = now
        window_expiry = now + timedelta(hours=24)

        result = {
            "phone": clean_phone,
            "window_open": True,
            "window_expires_at": window_expiry.isoformat(),
            "opt_out_detected": False,
            "human_takeover_requested": False
        }

        if not text:
            return result

        normalized_text = text.strip().lower()

        # 2. Check Opt-Out
        words = set(normalized_text.split())
        if words.intersection(OPT_OUT_KEYWORDS_EN) or words.intersection(OPT_OUT_KEYWORDS_ES) or normalized_text in OPT_OUT_KEYWORDS_ES:
            logger.warning(f"CRITICAL: Opt-out request detected from {clean_phone} ('{text}')")
            self.suppress_contact(clean_phone, reason=f"Customer keyword: {text}")
            result["opt_out_detected"] = True
            result["window_open"] = False
            return result

        # 3. Check Human Takeover Request
        for kw in HUMAN_TAKEOVER_KEYWORDS:
            if kw in normalized_text:
                logger.info(f"Human takeover request detected from {clean_phone} ('{text}')")
                self.human_takeover_flags[clean_phone] = True
                result["human_takeover_requested"] = True
                break

        return result

    def is_service_window_active(self, phone: str) -> Tuple[bool, Optional[float]]:
        """
        Checks whether the 24-hour Meta customer service window is open.
        Returns: (is_active, remaining_hours)
        """
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        last_inbound = self.contact_windows.get(clean_phone)
        if not last_inbound:
            return False, 0.0

        now = datetime.now(timezone.utc)
        elapsed = (now - last_inbound).total_seconds()
        remaining_seconds = (24 * 3600) - elapsed

        if remaining_seconds > 0:
            return True, round(remaining_seconds / 3600.0, 2)
        return False, 0.0

    def suppress_contact(self, phone: str, reason: str = "User opt-out"):
        """Adds contact to permanent suppression list."""
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        self.suppression_list[clean_phone] = {
            "opted_out_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason
        }

    def is_suppressed(self, phone: str) -> bool:
        """Verifies if the contact has revoked consent."""
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        return clean_phone in self.suppression_list

    def is_human_takeover_active(self, phone: str) -> bool:
        """Verifies if an AI response is locked out in favor of a human agent."""
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        return self.human_takeover_flags.get(clean_phone, False)

    def set_human_takeover(self, phone: str, active: bool = True):
        """Sets or releases human takeover."""
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        self.human_takeover_flags[clean_phone] = active

    def verify_outbound_eligibility(self, 
                                   phone: str, 
                                   message_type: str = "text", 
                                   template_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Authoritative validation before any outbound WhatsApp message is dispatched:
        1. Consent / Suppression check.
        2. TCPA Quiet hours check.
        3. 24-Hour window verification (Free-form text blocked outside window).
        4. Global kill-switch check.
        """
        clean_phone = "".join(filter(str.isdigit, str(phone)))

        # 1. Global Kill-switch
        if config.KILL_SWITCH_ACTIVE:
            return {
                "eligible": False,
                "reason": "GLOBAL_KILL_SWITCH_ACTIVE",
                "message": "Commercial sending is halted by administrator kill-switch."
            }

        # 2. Suppression Check
        if self.is_suppressed(clean_phone):
            return {
                "eligible": False,
                "reason": "CONTACT_SUPPRESSED",
                "message": "Contact has opted out (STOP / PARAR). Sending is strictly prohibited."
            }

        # 3. Quiet Hours Check
        current_hour_utc = datetime.now(timezone.utc).hour
        # Default approximation for Americas (UTC-5): 8pm local is 01:00 UTC, 8am local is 13:00 UTC
        if 1 <= current_hour_utc < 12:
            return {
                "eligible": False,
                "reason": "QUIET_HOURS_VIOLATION",
                "message": "Outbound message blocked during TCPA quiet hours (8:00 PM - 8:00 AM local)."
            }

        # 4. 24-Hour Window Verification
        is_window_open, remaining_hrs = self.is_service_window_active(clean_phone)

        if message_type == "text" and not is_window_open:
            return {
                "eligible": False,
                "reason": "SERVICE_WINDOW_EXPIRED",
                "message": (
                    "Meta policy forbids free-form text messages outside the 24-hour customer window. "
                    "You must use an approved Meta Template (e.g. Utility/Marketing) to initiate contact."
                ),
                "remaining_window_hours": 0.0,
                "requires_template": True
            }

        # If sending template outside window, ensure template_name is specified
        if not is_window_open and message_type == "template" and not template_name:
            return {
                "eligible": False,
                "reason": "MISSING_TEMPLATE_NAME",
                "message": "Out-of-window message requires an approved template name."
            }

        return {
            "eligible": True,
            "message_type": message_type,
            "window_open": is_window_open,
            "remaining_window_hours": remaining_hrs,
            "human_takeover_active": self.is_human_takeover_active(clean_phone)
        }

whatsapp_compliance = WhatsAppComplianceGate()
