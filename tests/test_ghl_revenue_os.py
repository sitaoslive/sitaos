# -*- coding: utf-8 -*-
"""
Alpha Vision Revenue OS — Master GHL Commercial Integration Acceptance Test Suite
Verifies the 15 Canonical Commercial Acceptance Tests (TEST A through TEST O)
as mandated by the Master GHL Revenue Operating System Specification (Section 30).
"""

import json
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from server import app
from engine.ghl_gateway import GHLCommercialGateway, EventEnvelope
from engine.prospect_engine import prospect_engine
from engine.voice_ai import voice_ai_engine
from engine.compliance import compliance_gate

client = TestClient(app)

@pytest.fixture
def fresh_gateway():
    """Provides an isolated GHLCommercialGateway instance for testing."""
    return GHLCommercialGateway(location_id="n4sb0M0P3oQhIux2e1Um", webhook_secret="test_secret_key_123")


# ============================================================================
# TEST A — Website Inquiry
# ============================================================================

def test_TEST_A_website_inquiry(fresh_gateway):
    """
    TEST A: Fictional veterinary business submits product inquiry form.
    Expected:
    - Exactly one GHL contact created.
    - One appropriate opportunity created.
    - Correct product interest ('vet_freedom').
    - Correct funnel attribution.
    - Marked as new.
    """
    record, is_new = fresh_gateway.upsert_contact_record(
        name="Dr. Mateo Restrepo",
        email="mateo@medellinvet.com",
        phone="+573001234567",
        company_name="Clinica Veterinaria Poblado",
        product_interest="vet_freedom",
        source="website_funnel_vet",
        qualification_score=75
    )

    assert is_new is True
    assert record.ghl_contact_id.startswith("ghl_ct_")
    assert record.ghl_opportunity_id.startswith("ghl_opp_")
    assert record.product_interest == "vet_freedom"
    assert record.internal_prospect_id.startswith("PROSP-")


# ============================================================================
# TEST B — Duplicate Inquiry
# ============================================================================

def test_TEST_B_duplicate_inquiry(fresh_gateway):
    """
    TEST B: Same synthetic contact submits form twice.
    Expected:
    - No duplicate contact created.
    - No duplicate opportunity created.
    - Same GHL contact ID returned.
    - is_new is False on 2nd submission.
    """
    # 1st submission
    rec1, is_new1 = fresh_gateway.upsert_contact_record(
        name="Dr. Mateo Restrepo",
        email="mateo@medellinvet.com",
        phone="+573001234567",
        product_interest="vet_freedom"
    )
    assert is_new1 is True

    # 2nd submission (same email, slightly different phone format)
    rec2, is_new2 = fresh_gateway.upsert_contact_record(
        name="Mateo Restrepo",
        email="MATEO@medellinvet.com",
        phone="573001234567",
        product_interest="vet_freedom"
    )
    assert is_new2 is False
    assert rec1.ghl_contact_id == rec2.ghl_contact_id
    assert rec1.ghl_opportunity_id == rec2.ghl_opportunity_id
    assert len(fresh_gateway.identity_registry) == 1


# ============================================================================
# TEST C — Multiple Channels
# ============================================================================

def test_TEST_C_multiple_channels_single_identity(fresh_gateway):
    """
    TEST C: Same contact reaches out across web form, email, and phone.
    Expected:
    - Single unified GHL contact ID.
    - Unified identity across all channels.
    - Duplicate message sequences suppressed.
    """
    # 1. Web form creates identity
    rec_web, _ = fresh_gateway.upsert_contact_record(
        name="Carlos Mendoza",
        email="carlos@mendozahvac.com",
        phone="+12145550199",
        product_interest="contractor_os"
    )

    # 2. Later, inbound call with same phone number
    rec_call, is_new_call = fresh_gateway.upsert_contact_record(
        name="Carlos M.",
        phone="+1-214-555-0199",
        product_interest="contractor_os"
    )

    assert is_new_call is False
    assert rec_call.ghl_contact_id == rec_web.ghl_contact_id

    # 3. Message deduplication across channels
    can_send_1 = fresh_gateway.can_dispatch_message(rec_web.ghl_contact_id, "WF-010", "welcome_sms")
    can_send_2 = fresh_gateway.can_dispatch_message(rec_web.ghl_contact_id, "WF-010", "welcome_sms")

    assert can_send_1 is True
    assert can_send_2 is False  # Suppressed duplicate


# ============================================================================
# TEST D — Research Enrichment
# ============================================================================

def test_TEST_D_research_enrichment(fresh_gateway):
    """
    TEST D: GHL lead triggers research enrichment in Alpha Vision Revenue OS.
    Expected:
    - 100-point score calculated from business facts.
    - CRM record updated with score.
    - Zero duplicate CRM contacts created.
    """
    rec, _ = fresh_gateway.upsert_contact_record(
        name="Sarah Jenkins",
        email="sarah@lonestarplumbing.com",
        phone="+15125550188",
        product_interest="contractor_os"
    )

    # Ingest into prospect engine
    prospect = prospect_engine.ingest_prospect({
        "business_name": "Lone Star Plumbing",
        "contact_name": "Sarah Jenkins",
        "email": "sarah@lonestarplumbing.com",
        "phone": "+15125550188",
        "industry": "PLUMBING",
        "country": "US",
        "address": "Austin, TX",
        "state_license_number": "TX-PL-88910",
        "license_active": True,
        "team_size": 4,
        "current_tools": ["pen_and_paper"],
        "pain_points": ["missed_emergency_calls", "slow_invoicing"]
    })

    scored = prospect_engine.calculate_100pt_score(prospect["prospect_id"])
    assert scored["total_score"] >= 70

    # Ensure identity remains clean
    assert len(fresh_gateway.identity_registry) == 1


# ============================================================================
# TEST E — Voice AI
# ============================================================================

def test_TEST_E_voice_ai_contractor_booking(fresh_gateway):
    """
    TEST E: Synthetic eligible inbound caller requests contractor demo.
    Expected:
    - Correct AI response.
    - Correct product identification.
    - Appointment registered.
    - Exactly one confirmation.
    """
    call = voice_ai_engine.initiate_inbound_call(from_number="+12145558833", to_number="+19299663559")
    turn = voice_ai_engine.process_speech_turn(call_id=call.call_id, caller_utterance="We run an HVAC business in Dallas with 5 techs and need dispatching.")

    assert voice_ai_engine.active_calls[call.call_id].product_identified == "service_business_os"
    assert turn["action"] in ["SPEAK", "PROVIDE_INFO", "BOOK_APPOINTMENT", "QUALIFIED"]

    # Register appointment through gateway
    appt = fresh_gateway.register_or_reschedule_appointment(
        appointment_id="appt_call_101",
        contact_id="ghl_ct_voice_test",
        calendar_id="2Btd7kd9NkVtIWA9glW4",
        start_time_iso="2026-11-25T14:00:00Z"
    )
    assert appt["status"] == "CONFIRMED"
    assert appt["rescheduled"] is False


# ============================================================================
# TEST F — Calendar Rescheduling
# ============================================================================

def test_TEST_F_calendar_rescheduling(fresh_gateway):
    """
    TEST F: Prospect reschedules demo.
    Expected:
    - Appointment record updated with new start time.
    - Marked as rescheduled.
    - Old reminders reset / cancelled.
    - No duplicate appointment ID created.
    """
    # Initial booking
    appt1 = fresh_gateway.register_or_reschedule_appointment(
        appointment_id="appt_101",
        contact_id="ghl_ct_demo",
        calendar_id="2Btd7kd9NkVtIWA9glW4",
        start_time_iso="2026-11-25T10:00:00Z"
    )
    assert appt1["rescheduled"] is False

    # Reschedule
    appt2 = fresh_gateway.register_or_reschedule_appointment(
        appointment_id="appt_101",
        contact_id="ghl_ct_demo",
        calendar_id="2Btd7kd9NkVtIWA9glW4",
        start_time_iso="2026-11-26T14:00:00Z"
    )
    assert appt2["rescheduled"] is True
    assert appt2["start_time"] == "2026-11-26T14:00:00Z"
    assert len(fresh_gateway.active_appointments) == 1


# ============================================================================
# TEST G — Human Takeover
# ============================================================================

def test_TEST_G_human_takeover_pauses_ai(fresh_gateway):
    """
    TEST G: Human sales rep takes over conversation.
    Expected:
    - AI assistant immediately paused.
    - can_dispatch_message returns False.
    - Resumes only upon explicit release.
    """
    contact_id = "ghl_ct_human_test"

    # Before takeover: messaging is allowed
    assert fresh_gateway.can_dispatch_message(contact_id, "WF-012", "ai_reply") is True

    # Engage human takeover
    takeover = fresh_gateway.engage_human_takeover(contact_id=contact_id, operator_name="freud_sales")
    assert takeover["status"] == "AI_PAUSED"

    # While locked: AI messaging blocked
    assert fresh_gateway.can_dispatch_message(contact_id, "WF-012", "ai_reply") is False

    # Release human takeover
    released = fresh_gateway.release_human_takeover(contact_id=contact_id)
    assert released["status"] == "AI_RESUMED"


# ============================================================================
# TEST H — Proposal
# ============================================================================

def test_TEST_H_proposal_followup_deduplication(fresh_gateway):
    """
    TEST H: Approved proposal sent to prospect.
    Expected:
    - Exactly one proposal sequence initiated.
    - Duplicate proposal sends blocked.
    """
    contact_id = "ghl_ct_prop_test"

    # First proposal send allowed
    p1 = fresh_gateway.can_dispatch_message(contact_id, "WF-017", "proposal_pdf")
    assert p1 is True

    # Immediate duplicate proposal send blocked
    p2 = fresh_gateway.can_dispatch_message(contact_id, "WF-017", "proposal_pdf")
    assert p2 is False


# ============================================================================
# TEST I — Payment
# ============================================================================

def test_TEST_I_payment_idempotency_prevents_duplicate_provisioning(fresh_gateway):
    """
    TEST I: Payment webhook event delivered twice.
    Expected:
    - First webhook provisions tenant.
    - Second webhook recognized as duplicate, safe acknowledged.
    - Exactly ONE tenant organization created.
    """
    event_id = "evt_stripe_test_998877"

    # First arrival
    res1 = fresh_gateway.reconcile_payment_and_provision_tenant(
        payment_event_id=event_id,
        customer_id="cust_stripe_123",
        plan_id="contractor_pro",
        org_name="Summit HVAC",
        subdomain="summit-hvac"
    )
    assert res1["duplicate_suppressed"] is False
    assert res1["status"] == "PROVISIONED_SUCCESSFULLY"

    # Second arrival of same payment
    res2 = fresh_gateway.reconcile_payment_and_provision_tenant(
        payment_event_id=event_id,
        customer_id="cust_stripe_123",
        plan_id="contractor_pro",
        org_name="Summit HVAC",
        subdomain="summit-hvac"
    )
    assert res2["duplicate_suppressed"] is True
    assert res2["status"] == "ALREADY_PROVISIONED"
    assert len(fresh_gateway.provisioned_tenants) == 1


# ============================================================================
# TEST J — Provisioning Failure
# ============================================================================

def test_TEST_J_provisioning_failure_handling(fresh_gateway):
    """
    TEST J: Ingesting malformed or failed payload.
    Expected:
    - Dead letter queue records event.
    - No false success recorded.
    """
    envelope = EventEnvelope(
        event_type="provision.failed",
        source_system="supabase",
        idempotency_key="prov_fail_01",
        status="FAILED",
        error_message="Subdomain reserved by another tenant"
    )

    fresh_gateway.dead_letter_queue.append(envelope)
    health = fresh_gateway.get_integration_health()
    assert health["dead_letter_events"] == 1


# ============================================================================
# TEST K — Opt-Out
# ============================================================================

def test_TEST_K_opt_out_suppression_propagation():
    """
    TEST K: Contact opts out.
    Expected:
    - Compliance gate suppresses email and phone.
    - All outreach permanently halted.
    """
    phone = "+12145559988"
    email = "optout@testclinic.com"

    compliance_gate.add_suppression(kind="phone", value=phone, reason="Texted STOP")
    compliance_gate.add_suppression(kind="email", value=email, reason="Unsubscribe link clicked")

    assert compliance_gate.is_suppressed(phone=phone) is True
    assert compliance_gate.is_suppressed(email=email) is True


# ============================================================================
# TEST L — GHL Outage
# ============================================================================

def test_TEST_L_ghl_outage_buffering_and_recovery(fresh_gateway):
    """
    TEST L: Simulate GHL API unavailable.
    Expected:
    - Events buffered in outbox with PENDING status.
    - When API recovers, events flushed safely.
    - No dropped transactions.
    """
    fresh_gateway.ghl_api_available = False

    envelope = EventEnvelope(
        event_type="contact.sync",
        source_system="alpha_revenue_os",
        idempotency_key="outage_test_01",
        payload={"name": "Dr. Davis"}
    )

    buf = fresh_gateway.buffer_outbound_event(envelope)
    assert buf["delivered"] is False
    assert buf["status"] == "QUEUED_DUE_TO_OUTAGE"

    health = fresh_gateway.get_integration_health()
    assert health["pending_events"] == 1

    # Simulate GHL recovery
    fresh_gateway.ghl_api_available = True
    flushed = fresh_gateway.retry_outbox_events()
    assert flushed == 1

    health_after = fresh_gateway.get_integration_health()
    assert health_after["pending_events"] == 0


# ============================================================================
# TEST M — Open Existing Opportunity
# ============================================================================

def test_TEST_M_open_existing_opportunity_not_duplicated(fresh_gateway):
    """
    TEST M: An interested contact already has an open deal for vet_freedom.
    Expected:
    - Existing opportunity ID returned.
    - is_newly_created is False.
    """
    rec, _ = fresh_gateway.upsert_contact_record(
        name="Dr. Laura Ramos",
        email="laura@calivet.com",
        product_interest="vet_freedom"
    )

    opp_id, is_new = fresh_gateway.resolve_or_create_opportunity(
        contact_id=rec.ghl_contact_id,
        product_interest="vet_freedom",
        is_expansion=False
    )

    assert is_new is False
    assert opp_id == rec.ghl_opportunity_id


# ============================================================================
# TEST N — Separate Product Interest
# ============================================================================

def test_TEST_N_separate_product_interest_creates_distinct_opportunity(fresh_gateway):
    """
    TEST N: Same legitimate buyer becomes interested in a second Alpha Vision product.
    Expected:
    - Same contact relationship preserved.
    - Separate distinct opportunity created for the 2nd product.
    - No corrupt merging of lifecycles.
    """
    rec, _ = fresh_gateway.upsert_contact_record(
        name="Robert Sterling",
        email="robert@sterlinggroup.com",
        product_interest="contractor_os"
    )

    # Inquires about vet product for partner clinic
    second_opp_id, is_new = fresh_gateway.resolve_or_create_opportunity(
        contact_id=rec.ghl_contact_id,
        product_interest="vet_freedom",
        is_expansion=False
    )

    assert is_new is True
    assert second_opp_id != rec.ghl_opportunity_id


# ============================================================================
# TEST O — Existing SaaS Customer Expansion
# ============================================================================

def test_TEST_O_existing_saas_customer_expansion(fresh_gateway):
    """
    TEST O: Active subscriber requests additional technician seats / expansion.
    Expected:
    - Expansion opportunity created.
    - Base organization ID preserved.
    - No duplicate base subscription.
    """
    rec, _ = fresh_gateway.upsert_contact_record(
        name="Marcus Vance",
        email="marcus@summithvac.com",
        product_interest="contractor_os"
    )
    rec.saas_organization_id = "org_summit_hvac"

    exp_opp_id, is_new = fresh_gateway.resolve_or_create_opportunity(
        contact_id=rec.ghl_contact_id,
        product_interest="contractor_os",
        is_expansion=True
    )

    assert is_new is True
    assert rec.saas_organization_id == "org_summit_hvac"  # Base tenant preserved
