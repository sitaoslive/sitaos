"""
Alpha Vision Revenue OS - Normalized WhatsApp Webhook Processor
Processes incoming Meta WhatsApp Webhook payloads (messages, delivery statuses, errors),
enforces signature verification, idempotency, compliance gating, GHL synchronization,
and optional Claude AI response assistance.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from engine.whatsapp_cloud import whatsapp_client
from engine.whatsapp_compliance import whatsapp_compliance
from engine.whatsapp_cost import whatsapp_cost
from engine.whatsapp_ghl_sync import whatsapp_ghl_sync

logger = logging.getLogger("whatsapp_webhook")
logger.setLevel(logging.INFO)

class WhatsAppWebhookProcessor:
    """Enterprise webhook ingestion engine for Meta WhatsApp Cloud API."""

    def __init__(self):
        # In-memory deduplication set for idempotency
        self.processed_message_ids = set()

    def process_raw_webhook(self, payload: Dict[str, Any], raw_body: bytes, signature_header: Optional[str]) -> Dict[str, Any]:
        """
        Main entry point for incoming Meta POST webhook:
        1. Verifies HMAC SHA-256 signature.
        2. Parses Meta object structure.
        3. Routes to message, status receipt, or error handler.
        """
        # 1. Signature Verification
        if not whatsapp_client.verify_signature(raw_body, signature_header):
            logger.error("Rejecting Meta Webhook: Invalid Signature.")
            return {"status": "error", "message": "Invalid HMAC SHA-256 signature", "code": 403}

        # 2. Check Payload Structure
        if payload.get("object") != "whatsapp_business_account":
            logger.warning(f"Ignored non-WABA webhook object: {payload.get('object')}")
            return {"status": "ignored", "reason": "Not a whatsapp_business_account event"}

        results = []
        entries = payload.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                field = change.get("field")
                value = change.get("value", {})
                if field == "messages":
                    res = self._handle_messages_change(value)
                    results.append(res)
                else:
                    logger.info(f"Unhandled Meta Webhook field: {field}")

        return {"status": "processed", "results": results}

    def _handle_messages_change(self, value: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts messages, statuses, or errors from the Meta 'messages' change object."""
        metadata = value.get("metadata", {})
        business_phone_id = metadata.get("phone_number_id")
        display_phone_number = metadata.get("display_phone_number")

        # 1. Handle Inbound Messages
        messages = value.get("messages", [])
        if messages:
            return self._process_inbound_messages(messages, value.get("contacts", []), business_phone_id)

        # 2. Handle Message Status Updates (sent, delivered, read, failed)
        statuses = value.get("statuses", [])
        if statuses:
            return self._process_statuses(statuses, business_phone_id)

        # 3. Handle Errors
        errors = value.get("errors", [])
        if errors:
            logger.error(f"Meta Webhook Error reported: {errors}")
            return {"status": "error_logged", "errors": errors}

        return {"status": "noop"}

    def _process_inbound_messages(self, 
                                  messages: List[Dict[str, Any]], 
                                  contacts: List[Dict[str, Any]], 
                                  business_phone_id: str) -> Dict[str, Any]:
        """Handles customer-initiated messages, idempotency, compliance, and CRM sync."""
        processed_count = 0
        contacts_map = {c.get("wa_id"): c.get("profile", {}).get("name") for c in contacts}

        for msg in messages:
            msg_id = msg.get("id")
            from_wa_id = msg.get("from")
            msg_type = msg.get("type")
            timestamp = msg.get("timestamp")
            customer_name = contacts_map.get(from_wa_id, f"WhatsApp User {from_wa_id[-4:]}")

            # Idempotency Check
            if msg_id in self.processed_message_ids:
                logger.info(f"Duplicate Meta message {msg_id} suppressed by idempotency filter.")
                continue
            self.processed_message_ids.add(msg_id)

            # Extract body based on type
            body_text = ""
            if msg_type == "text":
                body_text = msg.get("text", {}).get("body", "")
            elif msg_type == "button":
                body_text = msg.get("button", {}).get("text", "")
            elif msg_type == "interactive":
                body_text = msg.get("interactive", {}).get("button_reply", {}).get("title", "")
            else:
                body_text = f"[{msg_type.upper()} ATTACHMENT]"

            logger.info(f"Inbound WhatsApp from {from_wa_id} ({customer_name}): '{body_text}'")

            # 1. Compliance Registration & Opt-Out Detection
            comp_res = whatsapp_compliance.register_inbound_activity(from_wa_id, body_text)

            # If Opt-out requested
            if comp_res.get("opt_out_detected"):
                whatsapp_client.send_text_message(
                    to_phone=from_wa_id,
                    message_body="Has sido dado de baja exitosamente. No recibirás más mensajes de Alpha Vision. / You have been successfully unsubscribed."
                )
                whatsapp_cost.record_message_event(from_wa_id, "service", "sent")
                continue

            # 2. GHL CRM Matching & Synchronization
            ghl_match = whatsapp_ghl_sync.match_or_create_contact(
                phone=from_wa_id,
                name=customer_name
            )
            ghl_contact_id = ghl_match.get("ghl_contact_id")

            # Update GHL 24h Window & State
            whatsapp_ghl_sync.update_whatsapp_window_state(
                ghl_contact_id=ghl_contact_id,
                last_message_id=msg_id,
                window_expiry_iso=comp_res.get("window_expires_at"),
                state="HUMAN_TAKEOVER" if comp_res.get("human_takeover_requested") else "WINDOW_ACTIVE"
            )

            # If Human Takeover was requested, tag contact in GHL
            if comp_res.get("human_takeover_requested"):
                whatsapp_ghl_sync.set_human_takeover_tag(ghl_contact_id, active=True)
                whatsapp_client.send_text_message(
                    to_phone=from_wa_id,
                    message_body="Un especialista de nuestro equipo revisará tu mensaje en breve. Gracias por contactar a Alpha Vision."
                )
                whatsapp_cost.record_message_event(from_wa_id, "service", "sent")
                processed_count += 1
                continue

            # Send read receipt
            whatsapp_client.mark_as_read(msg_id)

            # Record telemetry & cost (Customer-initiated service message)
            whatsapp_cost.record_message_event(from_wa_id, "service", "delivered")
            processed_count += 1

        return {"status": "messages_processed", "count": processed_count}

    def _process_statuses(self, statuses: List[Dict[str, Any]], business_phone_id: str) -> Dict[str, Any]:
        """Handles delivery status receipts from Meta (sent, delivered, read, failed)."""
        updated_count = 0
        for st in statuses:
            msg_id = st.get("id")
            status = st.get("status")
            recipient_id = st.get("recipient_id")
            errors = st.get("errors")

            logger.info(f"WhatsApp Status Receipt: Msg {msg_id} -> {status.upper()} (Recipient: {recipient_id})")
            if errors:
                logger.error(f"WhatsApp Delivery Failure on msg {msg_id}: {errors}")

            updated_count += 1

        return {"status": "statuses_processed", "count": updated_count}

whatsapp_webhook_processor = WhatsAppWebhookProcessor()
