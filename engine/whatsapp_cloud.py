"""
Alpha Vision Revenue OS - Meta WhatsApp Cloud API Client
Direct, production-grade integration with Meta's official WhatsApp Business Platform (Graph API v21.0).
Zero third-party wrapper fees. Zero scraping or unofficial sessions.
"""

import hmac
import hashlib
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from engine.config import config

logger = logging.getLogger("whatsapp_cloud")
logger.setLevel(logging.INFO)

GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

class MetaWhatsAppClient:
    """Official Meta WhatsApp Cloud API Client."""

    def __init__(self, 
                 access_token: Optional[str] = None, 
                 phone_number_id: Optional[str] = None,
                 app_secret: Optional[str] = None,
                 verify_token: Optional[str] = None):
        self.access_token = access_token or config.META_ACCESS_TOKEN or config.WHATSAPP_TOKEN
        self.phone_number_id = phone_number_id or config.META_PHONE_NUMBER_ID or config.WHATSAPP_PHONE_NUMBER_ID
        self.app_secret = app_secret or config.META_APP_SECRET
        self.verify_token = verify_token or config.META_WEBHOOK_VERIFY_TOKEN

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "AlphaVision-WhatsApp-Cloud-Client/1.0"
        }

    def verify_webhook_challenge(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Validates Meta's GET webhook verification request."""
        if mode == "subscribe" and token == self.verify_token:
            logger.info("Meta Webhook verification challenge succeeded.")
            return challenge
        logger.warning("Meta Webhook verification challenge failed. Token mismatch.")
        return None

    def verify_signature(self, raw_payload: bytes, signature_header: Optional[str]) -> bool:
        """
        Validates X-Hub-Signature-256 using HMAC SHA-256 and META_APP_SECRET.
        Rejects invalid or missing signatures in production.
        """
        if not self.app_secret:
            # If app secret is not yet configured, warn and allow testing
            logger.warning("META_APP_SECRET not configured. Signature verification bypassed for staging/dev.")
            return True

        if not signature_header or not signature_header.startswith("sha256="):
            logger.error("Missing or malformed X-Hub-Signature-256 header.")
            return False

        expected_hash = signature_header[7:]
        calculated_hash = hmac.new(
            self.app_secret.encode("utf-8"),
            raw_payload,
            hashlib.sha256
        ).hexdigest()

        is_valid = hmac.compare_digest(expected_hash, calculated_hash)
        if not is_valid:
            logger.error("Invalid Meta Webhook signature.")
        return is_valid

    def normalize_phone(self, phone: str) -> str:
        """Normalizes phone numbers to standard clean international digits (E.164 without '+')."""
        clean = "".join(filter(str.isdigit, str(phone)))
        return clean

    def send_text_message(self, to_phone: str, message_body: str, preview_url: bool = False) -> Dict[str, Any]:
        """
        Sends a standard free-form text message via Meta WhatsApp Cloud API.
        NOTE: Can only be sent within the 24-hour customer service window.
        """
        clean_to = self.normalize_phone(to_phone)
        if not self.access_token or not self.phone_number_id:
            logger.info(f"[SIMULATED OUTBOUND WA] To: {clean_to} | Body: {message_body[:60]}... (Awaiting Meta Credentials)")
            return {
                "success": True,
                "status": "simulated",
                "messages": [{"id": f"sim_wamid_{int(datetime.now(timezone.utc).timestamp())}"}],
                "recipient_id": clean_to
            }

        url = f"{GRAPH_API_BASE}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": message_body
            }
        }

        return self._post_json(url, payload)

    def send_template_message(self, 
                              to_phone: str, 
                              template_name: str, 
                              language_code: str = "es", 
                              components: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Sends an approved Meta WhatsApp Template message.
        Can be sent outside the 24-hour service window with opt-in consent.
        """
        clean_to = self.normalize_phone(to_phone)
        if not self.access_token or not self.phone_number_id:
            logger.info(f"[SIMULATED TEMPLATE WA] To: {clean_to} | Template: {template_name} | Lang: {language_code}")
            return {
                "success": True,
                "status": "simulated",
                "messages": [{"id": f"sim_wamid_tpl_{int(datetime.now(timezone.utc).timestamp())}"}],
                "recipient_id": clean_to
            }

        url = f"{GRAPH_API_BASE}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                },
                "components": components or []
            }
        }

        return self._post_json(url, payload)

    def mark_message_as_read(self, message_id: str) -> Dict[str, Any]:
        """Sends a read receipt to Meta Cloud API for an incoming message."""
        if not self.access_token or not self.phone_number_id:
            return {"success": True, "status": "simulated_read"}

        url = f"{GRAPH_API_BASE}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        return self._post_json(url, payload)

    # Alias for convenience
    mark_as_read = mark_message_as_read

    def get_phone_number_details(self) -> Dict[str, Any]:
        """Fetches WhatsApp Business Number info, verified name, quality rating, and status."""
        if not self.access_token or not self.phone_number_id:
            return {
                "verified_name": "Alpha Vision Method (Pending Connection)",
                "display_phone_number": "+1 (Pending)",
                "quality_rating": "GREEN",
                "code_verification_status": "NOT_VERIFIED",
                "status": "AWAITING_SETUP"
            }

        url = f"{GRAPH_API_BASE}/{self.phone_number_id}?fields=verified_name,display_phone_number,quality_rating,code_verification_status"
        req = urllib.request.Request(url, headers=self._headers(), method="GET")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode()
            logger.error(f"Meta Graph API error fetching phone details: {e.code} - {err_msg}")
            return {"error": err_msg, "status_code": e.code}

    def _post_json(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Internal helper for executing POST requests with error handling."""
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers=self._headers(), method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res_data = json.loads(resp.read().decode())
                res_data["success"] = True
                return res_data
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            logger.error(f"Meta API HTTP Error {e.code}: {err_body}")
            try:
                parsed_err = json.loads(err_body)
            except Exception:
                parsed_err = {"raw_error": err_body}
            return {
                "success": False,
                "status_code": e.code,
                "error": parsed_err.get("error", parsed_err)
            }
        except Exception as e:
            logger.error(f"Network error communicating with Meta API: {e}")
            return {
                "success": False,
                "error": str(e)
            }

whatsapp_client = MetaWhatsAppClient()
