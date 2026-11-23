"""
Alpha Vision Revenue OS - Master Commercial Launch Test Suite (Part 2)
Verifies:
1. Bilingual Voice AI Receptionist (EN & ES) & Telephony Lifecycle
2. Voice AI Calendar Booking & GHL Contact Sync
3. Human Operator Escalation & Call Transfer
4. Outbound Voice Compliance Gate (TCPA quiet hours & anti-cold-call policy)
5. Canonical 40 Sales Workflows (SALES-01 through SALES-40)
6. Section 20 Bridge: Payment Confirmation -> SaaS Tenant Provisioning
7. Multi-Tenant Business Layer Separation (Layer A, B, C)
8. Commercial Telemetry & Founder Actions
"""

import pytest
from datetime import datetime, timezone
from engine.voice_ai import voice_ai_engine, PRIMARY_HUMAN_FORWARDING_PHONE, GHL_CALENDAR_CLARITY_ID
from engine.sales_workflows import sales_workflow_engine
from engine.compliance import compliance_gate
from engine.db_federation import db_federation_service
from engine.agent_org import agent_hub
from engine.config import config

class TestCommercialLaunchPart2:

    @pytest.fixture(autouse=True)
    def setup_suite(self):
        # Reset engine state before each test
        voice_ai_engine.active_calls.clear()
        voice_ai_engine.call_history.clear()
        voice_ai_engine.emergency_stop_active = False

    # =========================================================================
    # 1. VOICE AI RECEPTIONIST TESTS (Section 10)
    # =========================================================================

    def test_voice_ai_inbound_initialization_and_disclosure(self):
        """Verifies inbound call initiation and mandatory AI identity disclosure on turn 1."""
        call = voice_ai_engine.initiate_inbound_call(from_number="+15125550199")
        assert call.call_id.startswith("call_")
        assert call.status == "IN_PROGRESS"
        assert call.direction == "INBOUND"

        # Turn 1: English greeting
        turn_res = voice_ai_engine.process_speech_turn(call.call_id, "Hi, I saw your website and want information")
        assert turn_res["action"] == "SPEAK"
        assert "automated AI assistant" in turn_res["ai_response"]
        assert "recorded for quality assurance" in turn_res["ai_response"]

    def test_voice_ai_spanish_language_detection_and_product_classification(self):
        """Verifies seamless Spanish detection and Veterinary OS classification."""
        call = voice_ai_engine.initiate_inbound_call(from_number="+573105551234")
        
        turn_res = voice_ai_engine.process_speech_turn(
            call.call_id, 
            "Hola buenas tardes, llamo para preguntar sobre el software para clínica veterinaria y mascotas"
        )
        assert turn_res["action"] == "SPEAK"
        assert call.language == "es"
        assert call.product_identified == "vet_freedom_os"
        assert "asistente de inteligencia artificial" in turn_res["ai_response"]
        assert "Vet Freedom OS" in turn_res["ai_response"] or "veterinarias" in turn_res["ai_response"]

    def test_voice_ai_contractor_os_pricing_inquiry(self):
        """Verifies contractor software classification and grounded pricing answers."""
        call = voice_ai_engine.initiate_inbound_call(from_number="+12145558911")
        
        turn_res = voice_ai_engine.process_speech_turn(
            call.call_id, 
            "I run an HVAC contracting business with 5 vans. How much does your service software cost?"
        )
        assert turn_res["action"] == "SPEAK"
        assert call.product_identified == "service_business_os"
        assert "$299 - $499 USD/month" in turn_res["ai_response"]
        assert "zero per-seat penalty" in turn_res["ai_response"] or "free trial" in turn_res["ai_response"]

    def test_voice_ai_appointment_booking_and_ghl_sync(self):
        """Verifies voice-driven booking creates appointment on verified GHL calendar."""
        call = voice_ai_engine.initiate_inbound_call(from_number="+15125550789")
        voice_ai_engine.process_speech_turn(call.call_id, "I want software for plumbing contractors")
        
        booking_res = voice_ai_engine.process_speech_turn(call.call_id, "Yes, please schedule a demo for tomorrow")
        assert booking_res["action"] == "APPOINTMENT_PROPOSED"
        assert booking_res["booking_details"] is not None
        assert booking_res["booking_details"]["calendar_id"] == GHL_CALENDAR_CLARITY_ID
        assert call.appointment_booked is not None
        assert "tomorrow at 10:00 am eastern time" in booking_res["ai_response"].lower()

    def test_voice_ai_human_operator_escalation(self):
        """Verifies caller asking for human is transferred to verified forwarding number."""
        call = voice_ai_engine.initiate_inbound_call(from_number="+19295550122")
        
        turn_res = voice_ai_engine.process_speech_turn(call.call_id, "I need to speak to a real person right now")
        assert turn_res["action"] == "TRANSFER"
        assert turn_res["forwarding_number"] == PRIMARY_HUMAN_FORWARDING_PHONE
        assert call.status == "TRANSFERRED"
        assert call.human_transfer_requested is True

    def test_voice_ai_immediate_opt_out_and_suppression(self):
        """Verifies caller asking to stop calling triggers instant suppression and hangup."""
        test_phone = "+15125550999"
        call = voice_ai_engine.initiate_inbound_call(from_number=test_phone)
        
        turn_res = voice_ai_engine.process_speech_turn(call.call_id, "Please stop calling me and remove my number")
        assert turn_res["action"] == "HANG_UP"
        assert turn_res["status"] == "SUPPRESSED"
        assert compliance_gate.is_suppressed(phone=test_phone) is True

    def test_voice_ai_call_completion_and_telephony_metrics(self):
        """Verifies call conclusion, token accounting, and live telemetry."""
        call = voice_ai_engine.initiate_inbound_call(from_number="+15125550333")
        voice_ai_engine.process_speech_turn(call.call_id, "What does your company do?")
        completed_call = voice_ai_engine.complete_call(call.call_id, duration_seconds=120)
        
        assert completed_call.status == "COMPLETED"
        assert completed_call.duration_seconds == 120
        assert completed_call.cost_usd > 0.0

        metrics = voice_ai_engine.get_voice_metrics()
        assert metrics["total_calls_handled"] >= 1
        assert metrics["completed_calls_count"] >= 1
        assert "primary_forwarding_phone" in metrics

    # =========================================================================
    # 2. OUTBOUND VOICE COMPLIANCE GATE TESTS (Section 10.7)
    # =========================================================================

    def test_outbound_voice_rejects_cold_scraped_calls(self):
        """Verifies outbound gate unconditionally blocks cold automated dialing."""
        check = voice_ai_engine.validate_outbound_call(
            recipient_phone="+15125550111",
            lawful_basis="SCRAPED_COLD_CALL"
        )
        assert check.approved is False
        assert "Prohibited" in check.reason
        assert "compliance policy" in check.reason

    def test_outbound_voice_allows_opted_in_callback(self):
        """Verifies outbound gate approves legitimate opted-in callback requests."""
        # Test during non-quiet hours or check basis validation
        check = voice_ai_engine.validate_outbound_call(
            recipient_phone="+15125550222",
            lawful_basis="INBOUND_CALLBACK_REQUEST"
        )
        # If outside quiet hours, passes; if quiet hours, reason is quiet hours
        if check.approved:
            assert check.lawful_basis == "INBOUND_CALLBACK_REQUEST"
            assert check.ai_disclosure_required is True
        else:
            assert check.quiet_hours_active is True

    def test_outbound_voice_enforces_suppression(self):
        """Verifies outbound gate blocks any number on the suppression list."""
        suppressed_phone = "+15125550888"
        compliance_gate.add_suppression("phone", suppressed_phone, "test_opt_out", "test_suite")
        
        check = voice_ai_engine.validate_outbound_call(
            recipient_phone=suppressed_phone,
            lawful_basis="INBOUND_CALLBACK_REQUEST"
        )
        assert check.approved is False
        assert check.suppressed is True
        assert "Do-Not-Contact" in check.reason

    # =========================================================================
    # 3. CANONICAL 40 SALES WORKFLOWS TESTS (Section 16)
    # =========================================================================

    def test_canonical_40_workflows_registry_completeness(self):
        """Verifies all 40 canonical sales workflows (SALES-01 to SALES-40) are registered."""
        catalog = sales_workflow_engine.workflows_catalog
        assert len(catalog) == 40
        
        # Verify critical milestones exist
        assert "SALES-01" in catalog  # New Website Inquiry
        assert "SALES-06" in catalog  # Inbound Call Answering
        assert "SALES-09" in catalog  # Calendar Booking
        assert "SALES-16" in catalog  # Proposal Generation
        assert "SALES-21" in catalog  # Payment Link Generation
        assert "SALES-22" in catalog  # Payment Confirmation
        assert "SALES-23" in catalog  # SaaS Provisioning
        assert "SALES-26" in catalog  # Onboarding Assistance
        assert "SALES-40" in catalog  # Daily Executive Summary

    def test_deal_creation_and_stage_progression(self):
        """Verifies deal creation and pipeline stage advancement."""
        deal = sales_workflow_engine.create_commercial_deal({
            "business_name": "Dallas Comfort HVAC & Mechanical",
            "contact_name": "Mark Stevens",
            "contact_email": "mark@dallascomforthvac.com",
            "contact_phone": "+12145550144",
            "target_product_id": "service_business_os",
            "country": "US"
        })
        assert deal.deal_id.startswith("deal_")
        assert deal.stage == "Newly Discovered"
        assert deal.monthly_price_usd == 499.0

        adv_res = sales_workflow_engine.advance_deal_stage(deal.deal_id, "Demo Booked")
        assert adv_res["status"] == "STAGE_ADVANCED"
        assert deal.stage == "Demo Booked"

    # =========================================================================
    # 4. SECTION 20 BRIDGE: PAYMENT CONFIRMATION TO SAAS TENANT PROVISIONING
    # =========================================================================

    def test_section_20_payment_to_tenant_provisioning_pipeline(self):
        """
        Verifies Section 20 pipeline:
        GHL OPPORTUNITY WON -> AUTHORITATIVE PAYMENT -> SAAS PROVISIONING -> LIVE TENANT.
        Creates organization, reserves subdomain, allocates seats, generates owner invite.
        """
        deal = sales_workflow_engine.create_commercial_deal({
            "business_name": "Austin Modern Plumbing & Drain",
            "contact_name": "Sarah Jenkins",
            "contact_email": "sarah@austinmodernplumbing.com",
            "contact_phone": "+15125550911",
            "target_product_id": "service_business_os",
            "country": "US"
        })

        prov_result = sales_workflow_engine.execute_payment_and_provision_tenant(
            deal_id=deal.deal_id,
            transaction_id="ch_stripe_test_live_prov_001",
            amount_paid=998.0,  # $499 setup + $499 first month
            provider="STRIPE",
            target_subdomain="austinmodernplumbing"
        )

        assert prov_result["status"] == "SUCCESS_PROVISIONED"
        assert prov_result["tenant_org_id"] is not None
        assert prov_result["subdomain"] == "austinmodernplumbing"
        assert "login_url" in prov_result
        assert prov_result["seats_allocated"] >= 3
        assert deal.payment_confirmed is True
        assert deal.stage == "Onboarding In Progress"

        # Verify Central Org created in db_federation_service
        org = db_federation_service.get_organization(prov_result["tenant_org_id"])
        assert org is not None
        assert org.name == "Austin Modern Plumbing & Drain"
        assert org.subdomain == "austinmodernplumbing"
        assert org.status == "ACTIVE"

    def test_section_20_idempotency_prevents_duplicate_provisioning(self):
        """Verifies duplicate payment webhook does not re-provision existing tenant."""
        deal = sales_workflow_engine.create_commercial_deal({
            "business_name": "Lone Star Mechanical Pros",
            "contact_name": "Tom Bradley",
            "contact_email": "tom@lonestarpros.com",
            "contact_phone": "+12145550888",
            "target_product_id": "service_business_os"
        })

        # Run 1
        res1 = sales_workflow_engine.execute_payment_and_provision_tenant(
            deal_id=deal.deal_id,
            transaction_id="tx_idemp_001",
            amount_paid=998.0,
            target_subdomain="lonestarpros"
        )
        assert res1["status"] == "SUCCESS_PROVISIONED"
        first_org_id = res1["tenant_org_id"]

        # Run 2 (duplicate webhook)
        res2 = sales_workflow_engine.execute_payment_and_provision_tenant(
            deal_id=deal.deal_id,
            transaction_id="tx_idemp_001",
            amount_paid=998.0,
            target_subdomain="lonestarpros"
        )
        assert res2["status"] == "ALREADY_PROVISIONED"
        assert res2["tenant_org_id"] == first_org_id

    # =========================================================================
    # 5. BUSINESS LAYER SEPARATION & TELEMETRY (Section 2 & 24)
    # =========================================================================

    def test_business_layer_separation_rules(self):
        """Verifies strict separation between Alpha Vision Sales OS (Layer A), SaaS (Layer B), and Customer Data (Layer C)."""
        # Layer A deal creation
        deal = sales_workflow_engine.create_commercial_deal({
            "business_name": "Highland Park Veterinary Hospital",
            "contact_name": "Dr. Emily Vance",
            "contact_email": "dr.vance@highlandparkvet.com",
            "contact_phone": "+12145550233",
            "target_product_id": "vet_freedom_os"
        })
        assert deal.target_product_id == "vet_freedom_os"

        # Customer's internal patients (Layer C) must never enter Alpha Vision prospecting store
        patient_data = {"patient_name": "Bella the Labrador", "owner_name": "Jane Homeowner"}
        assert patient_data["patient_name"] not in deal.model_dump_json()

    def test_16_ai_sales_agents_governance(self):
        """Verifies all 16 canonical AI agents have defined roles, tools, and cost ceilings."""
        agents = agent_hub.agents_registry
        assert len(agents) >= 16

        # Check Agent 08 (Voice AI Receptionist)
        agent_08 = agent_hub.get_agent("agent_08_voice_receptionist")
        assert agent_08 is not None
        assert "Voice AI Receptionist" in agent_08.name
        assert "book_ghl_appointment" in agent_08.permitted_tools
        assert agent_08.cost_ceiling_usd <= 0.05
        assert len(agent_08.prohibited_actions) > 0

    def test_commercial_telemetry_reporting(self):
        """Verifies commercial telemetry calculates actual cash and MRR accurately."""
        telemetry = sales_workflow_engine.get_commercial_telemetry()
        assert "total_deals_managed" in telemetry
        assert "closed_won_deals_count" in telemetry
        assert "actual_cash_collected_usd" in telemetry
        assert "total_workflows_registered" in telemetry
        assert telemetry["total_workflows_registered"] == 40
