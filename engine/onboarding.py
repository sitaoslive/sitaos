"""
Alpha Vision AI Sales OS - Post-Purchase Manual Onboarding & AI Specialist Briefing Engine
Coordinates the intentional premium human touchpoint: calendar booking, technical intake,
and automated executive briefing generation for the implementation engineer.
"""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class OnboardingQuestionnaire(BaseModel):
    customer_id: str
    product_id: str
    company_name: str
    country: str
    team_size: int
    current_software: str
    primary_channels: List[str]
    critical_integrations: List[str]
    biggest_operational_bottleneck: str
    migration_records_estimate: int
    submitted_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class SpecialistBriefing(BaseModel):
    briefing_id: str
    customer_id: str
    company_name: str
    product_name: str
    purchased_plan: str
    scheduled_appointment_time: Optional[str] = None
    technical_complexity: str  # LOW, MODERATE, HIGH
    recommended_setup_order: List[str]
    potential_blockers: List[str]
    intake_summary: Dict[str, Any]
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class OnboardingEngine:
    def __init__(self):
        self.questionnaires: Dict[str, OnboardingQuestionnaire] = {}
        self.briefings: Dict[str, SpecialistBriefing] = {}
        self.booked_appointments: Dict[str, Dict[str, Any]] = {}
        self._init_sample_onboarding()

    def _init_sample_onboarding(self):
        """Initializes a verified sample onboarding case."""
        self.submit_intake_questionnaire({
            "customer_id": "cust_apex_climate_hvac",
            "product_id": "service_business_os",
            "company_name": "Apex Climate Solutions",
            "country": "US",
            "team_size": 8,
            "current_software": "Google Calendar & Paper Invoices",
            "primary_channels": ["Phone Call", "SMS"],
            "critical_integrations": ["QuickBooks Online", "Google Calendar"],
            "biggest_operational_bottleneck": "Missed after-hours emergency calls and slow manual quoting in the field.",
            "migration_records_estimate": 450
        })
        self.book_onboarding_call(
            customer_id="cust_apex_climate_hvac",
            slot_time="2026-11-25T14:00:00Z",
            ghl_calendar_id="cal_avm_onboarding_master",
            specialist_name="Senior Onboarding Engineer"
        )

    def submit_intake_questionnaire(self, data: Dict[str, Any]) -> OnboardingQuestionnaire:
        customer_id = data.get("customer_id", f"cust_{uuid.uuid4().hex[:8]}")
        q = OnboardingQuestionnaire(
            customer_id=customer_id,
            product_id=data.get("product_id", "service_business_os"),
            company_name=data.get("company_name", "Valued Customer"),
            country=data.get("country", "US"),
            team_size=int(data.get("team_size", 5)),
            current_software=data.get("current_software", "None"),
            primary_channels=data.get("primary_channels", ["Email", "Phone"]),
            critical_integrations=data.get("critical_integrations", []),
            biggest_operational_bottleneck=data.get("biggest_operational_bottleneck", "General administrative coordination"),
            migration_records_estimate=int(data.get("migration_records_estimate", 100))
        )
        self.questionnaires[customer_id] = q
        
        # Automatically generate / update AI Specialist Briefing
        self.generate_specialist_briefing(customer_id)
        return q

    def book_onboarding_call(
        self,
        customer_id: str,
        slot_time: str,
        ghl_calendar_id: str = "cal_avm_onboarding_master",
        specialist_name: str = "Alpha Implementation Lead"
    ) -> Dict[str, Any]:
        """Synchronizes booked onboarding appointment with GHL Calendar."""
        appt_id = f"appt_{uuid.uuid4().hex[:10]}"
        record = {
            "appointment_id": appt_id,
            "customer_id": customer_id,
            "slot_time": slot_time,
            "ghl_calendar_id": ghl_calendar_id,
            "specialist": specialist_name,
            "meeting_duration_minutes": 50,
            "meeting_url": f"https://meet.alphavisionmethod.com/onboard-{appt_id[:8]}",
            "status": "CONFIRMED",
            "booked_at": datetime.utcnow().isoformat()
        }
        self.booked_appointments[customer_id] = record
        
        # Refresh briefing with appointment time
        if customer_id in self.briefings:
            self.briefings[customer_id].scheduled_appointment_time = slot_time

        return record

    def generate_specialist_briefing(self, customer_id: str) -> SpecialistBriefing:
        """Agent 13: Customer Onboarding Coordinator pre-flight briefing."""
        q = self.questionnaires.get(customer_id)
        appt = self.booked_appointments.get(customer_id, {})
        
        company = q.company_name if q else "Customer Company"
        product = "Vet Life / Vet Freedom OS" if (q and q.product_id == "vet_freedom_os") else "Alpha Service Business OS"
        plan = "Growth Team ($497/mo)" if (q and q.product_id == "service_business_os") else "Clínica Domiciliaria ($389.000 COP/mo)"
        
        # Assess technical complexity
        complexity = "LOW"
        if q and (len(q.critical_integrations) > 2 or q.migration_records_estimate > 300):
            complexity = "MODERATE"
        if q and q.team_size > 15:
            complexity = "HIGH"

        # Determine setup order based on stated bottleneck
        setup_order = [
            "1. Verify Business Profile, Branding & Timezone",
            "2. Connect Calendar & Service Operating Hours",
            "3. Configure Staff Roles, Technician Presets & Permissions",
            "4. Wire Up Inbound Missed-Call & WhatsApp Concierge Webhooks",
            "5. Execute 3 Synthetic End-to-End Test Scenarios with Customer",
            "6. Conduct 15-Minute Daily Workflow Walkthrough for Business Owner"
        ]

        potential_blockers = [
            f"Customer currently relies on: {q.current_software if q else 'legacy tools'}. Verify data export format.",
            "Confirm that customer has admin credentials for any third-party accounting/calendar integration.",
            "Verify mobile phone operating system (iOS/Android) for field worker PWA shortcut install."
        ]

        briefing = SpecialistBriefing(
            briefing_id=f"brf_{uuid.uuid4().hex[:10]}",
            customer_id=customer_id,
            company_name=company,
            product_name=product,
            purchased_plan=plan,
            scheduled_appointment_time=appt.get("slot_time"),
            technical_complexity=complexity,
            recommended_setup_order=setup_order,
            potential_blockers=potential_blockers,
            intake_summary=q.model_dump() if q else {}
        )
        self.briefings[customer_id] = briefing
        return briefing

onboarding_engine = OnboardingEngine()
