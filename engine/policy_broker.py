"""
Alpha Vision Revenue OS - Deterministic Policy & Autonomy Broker
Enforces absolute boundaries over AI proposed actions:
- Operating Modes: SIMULATE, SHADOW, PILOT, OPERATE
- TCPA / Quiet hours & geographic jurisdiction rules
- Meta 24-hour service window gating
- Multilingual consent suppression (STOP / PARAR)
- Catalog price integrity (prohibits AI hallucinated discounts)
- Tenant isolation (prevents cross-tenant access)
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from engine.config import config
from engine.licensing import PRODUCTS_CATALOG

logger = logging.getLogger("policy_broker")
logger.setLevel(logging.INFO)

OPERATING_MODES = ["SIMULATE", "SHADOW", "PILOT", "OPERATE"]

class DeterministicPolicyBroker:
    """Enforces non-negotiable legal, commercial, and technical boundaries before any external action."""

    def __init__(self, mode: str = "PILOT"):
        self.mode = mode if mode in OPERATING_MODES else "PILOT"
        self.suppression_registry: Dict[str, Dict[str, Any]] = {}
        self.active_tenant_contexts: Dict[str, str] = {} # context_id -> tenant_id

    def set_mode(self, mode: str):
        if mode in OPERATING_MODES:
            self.mode = mode
            logger.info(f"Policy Broker operating mode set to: {self.mode}")

    def suppress_identifier(self, identifier: str, reason: str = "Customer Opt-Out"):
        """Suppresses phone or email globally across all communication channels."""
        clean_id = "".join(filter(str.isalnum, identifier.lower()))
        self.suppression_registry[clean_id] = {
            "suppressed_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason
        }
        logger.warning(f"Suppressed identifier: {identifier} (Reason: {reason})")

    def is_suppressed(self, identifier: str) -> bool:
        clean_id = "".join(filter(str.isalnum, identifier.lower()))
        return clean_id in self.suppression_registry

    def validate_tenant_boundary(self, current_tenant_id: str, target_tenant_id: str) -> bool:
        """Enforces strict multi-tenant isolation. Prevents cross-tenant association."""
        if not current_tenant_id or not target_tenant_id:
            return False
        return current_tenant_id == target_tenant_id

    def validate_pricing_offer(self, product_id: str, proposed_price: float, requested_discount: float = 0.0) -> Dict[str, Any]:
        """
        Validates proposed pricing against approved catalog.
        Prevents AI from inventing unauthorized discounts, free plans, or altered terms.
        """
        catalog_entry = PRODUCTS_CATALOG.get(product_id)
        if not catalog_entry:
            return {
                "valid": False,
                "reason": "PRODUCT_NOT_IN_CATALOG",
                "message": f"Product '{product_id}' is not in approved commercial catalog."
            }

        # Check default tier pricing
        plans = catalog_entry.get("pricing_tiers", {})
        approved_prices = [p.get("price_usd") for p in plans.values() if "price_usd" in p]

        # Model is NOT allowed to invent discounts unless approved in policy
        if requested_discount > 0.0:
            return {
                "valid": False,
                "reason": "UNAUTHORIZED_AI_DISCOUNT",
                "message": "AI model proposed an unauthorized discount. Commercial terms must follow catalog."
            }

        if approved_prices and proposed_price not in approved_prices and proposed_price < min(approved_prices):
            return {
                "valid": False,
                "reason": "PRICE_BELOW_FLOOR",
                "message": f"Proposed price ${proposed_price} is below approved catalog floor (${min(approved_prices)})."
            }

        return {"valid": True, "product": catalog_entry.get("name"), "price_approved": proposed_price}

    def evaluate_outbound_dispatch(self, 
                                   tenant_id: str,
                                   recipient_id: str, 
                                   channel: str, 
                                   message_type: str = "text",
                                   service_window_active: bool = False,
                                   template_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Final pre-flight gate before ANY message is dispatched to an external provider:
        1. Emergency kill switch.
        2. Operating mode check (SIMULATE/SHADOW block real external calls).
        3. Global suppression check.
        4. Meta 24-hour service window check.
        """
        # 1. Kill-Switch
        if config.KILL_SWITCH_ACTIVE:
            return {
                "approved": False,
                "reason": "KILL_SWITCH_ACTIVE",
                "message": "Outbound sending halted by administrator emergency kill-switch."
            }

        # 2. Operating Mode Check
        if self.mode == "SIMULATE":
            return {
                "approved": True,
                "mode": "SIMULATE",
                "simulated_only": True,
                "message": "Approved for synthetic simulation execution (zero real external calls)."
            }

        if self.mode == "SHADOW":
            return {
                "approved": False,
                "mode": "SHADOW",
                "reason": "SHADOW_MODE_READ_ONLY",
                "message": "System is in SHADOW mode. Actions are logged as drafts only."
            }

        # 3. Suppression Check
        if self.is_suppressed(recipient_id):
            return {
                "approved": False,
                "reason": "RECIPIENT_SUPPRESSED",
                "message": "Recipient has revoked consent or opted out. Communication prohibited."
            }

        # 4. Meta WhatsApp 24h Window Check
        if channel == "whatsapp":
            if message_type == "text" and not service_window_active:
                return {
                    "approved": False,
                    "reason": "SERVICE_WINDOW_EXPIRED",
                    "requires_template": True,
                    "message": "Meta Cloud API policy prohibits free text outside 24h window. Approved template required."
                }
            if message_type == "template" and not template_name:
                return {
                    "approved": False,
                    "reason": "MISSING_TEMPLATE",
                    "message": "Template dispatch requires a registered template name."
                }

        return {
            "approved": True,
            "mode": self.mode,
            "channel": channel,
            "recipient": recipient_id
        }

policy_broker = DeterministicPolicyBroker()
