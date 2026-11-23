"""
Alpha Vision AI Sales OS - Personalized Outreach & Quality Control Engine
Generates consultative, research-grounded sales copy and enforces strict message linting.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from engine.compliance import compliance_gate

class OutreachDraft(BaseModel):
    draft_id: str
    prospect_id: str
    channel: str  # email, whatsapp, linkedin
    language: str  # es, en
    subject: str
    body: str
    cited_observations: List[str]
    compliance_checks_passed: bool
    status: str = "PENDING_APPROVAL"  # PENDING_APPROVAL, APPROVED, REJECTED, DISPATCHED
    rejection_reason: Optional[str] = None

class OutreachEngine:
    def __init__(self):
        self.drafts_store: Dict[str, OutreachDraft] = {}
        self.banned_phrases = [
            "guaranteed 10x", "act now", "secret trick", "risk-free millions",
            "urgent opportunity", "limited spots left today", "unlimited free money"
        ]

    def lint_message(self, body: str, subject: str) -> Dict[str, Any]:
        """Scans sales copy for spam triggers, unsupported claims, and compliance footers."""
        combined = (subject + " " + body).lower()
        for phrase in self.banned_phrases:
            if phrase in combined:
                return {
                    "passed": False,
                    "reason": f"Contains prohibited spam/hype phrase: '{phrase}'"
                }

        # Check required opt-out mechanism
        if not ("unsubscribe" in combined or "cancelar" in combined or "responder 'baja'" in combined or "opt-out" in combined):
            return {
                "passed": False,
                "reason": "Missing mandatory opt-out / unsubscribe notice in message footer"
            }

        return {"passed": True}

    def generate_personalized_outreach(self, prospect: Dict[str, Any], demo_link: str) -> OutreachDraft:
        """Crafts bespoke, factual outreach copy referencing verified observations."""
        prospect_id = prospect.get("id", "lead_sample")
        business_name = prospect.get("business_name", "Your Business")
        dm_name = prospect.get("decision_maker_name", "") or ("Doctor/Doctora" if prospect.get("target_product_id") == "vet_freedom_os" else "Owner")
        country = prospect.get("country", "US")
        city = prospect.get("city", "your area")
        product_id = prospect.get("target_product_id", "service_business_os")
        evidence_list = prospect.get("evidence", [])
        
        cited_obs = [e.get("observation", "") if isinstance(e, dict) else e.observation for e in evidence_list[:2]]

        draft_id = f"draft_{prospect_id[:8]}"

        if product_id == "vet_freedom_os" or country in ["CO", "MX", "ES", "CL"]:
            # Spanish Veterinary / Latin America template
            obs_mention = f"Noté que trabajan con atención a domicilio en {city}."
            if cited_obs:
                obs_mention = f"Revisando los servicios de {business_name}, vi que coordinan visitas a domicilio y atención personalizada."
            
            subject = f"Una idea para organizar las visitas veterinarias de {business_name}"
            body = (
                f"Hola {dm_name},\n\n"
                f"{obs_mention}\n\n"
                f"Desarrollamos Vet Freedom OS, un sistema diseñado específicamente para veterinarios y clínicas móviles que necesitan "
                f"organizar citas en ruta, rastrear la llegada de auxiliares y enviar fórmulas médicas oficiales sin trabajo manual repetitivo.\n\n"
                f"Preparé una demostración interactiva con un caso real de una jornada de atención a domicilio para que veas cómo funciona en 2 minutos:\n"
                f"👉 {demo_link}\n\n"
                f"¿Te interesaría probarlo?\n\n"
                f"Saludos cordiales,\n"
                f"Daniela Morales\n"
                f"Alpha Vision Method · Sistemas Inteligentes de Operación\n\n"
                f"---\n"
                f"Si prefieres no recibir más ideas de optimización para tu consulta, solo responde 'cancelar' o 'baja' y no te volveremos a escribir."
            )
            language = "es"
        else:
            # English Service Business / North America template
            obs_mention = f"While researching top field service teams in {city}, I came across {business_name}."
            if cited_obs:
                obs_mention = f"Looking at {business_name}, I saw how you handle service inquiries and team dispatching."
            
            subject = f"Quick question about scheduling and lead response at {business_name}"
            body = (
                f"Hi {dm_name},\n\n"
                f"{obs_mention}\n\n"
                f"We build Alpha Service Business OS to help contractor and field service teams automatically capture missed customer calls, "
                f"dispatch technicians on live radar, and manage customer quotes from a single hub.\n\n"
                f"I set up a 2-minute interactive demo showing how an HVAC / trade company organizes jobs and field tech time-clocks:\n"
                f"👉 {demo_link}\n\n"
                f"Would you be open to exploring the interactive walkthrough?\n\n"
                f"Best regards,\n"
                f"Daniela Morales\n"
                f"Alpha Vision Method · Revenue Operations\n\n"
                f"---\n"
                f"If you'd rather not hear from us about software workflows, reply 'unsubscribe' and we will immediately remove {business_name}."
            )
            language = "en"

        lint_res = self.lint_message(body, subject)
        draft = OutreachDraft(
            draft_id=draft_id,
            prospect_id=prospect_id,
            channel="email",
            language=language,
            subject=subject,
            body=body,
            cited_observations=cited_obs,
            compliance_checks_passed=lint_res["passed"],
            status="PENDING_APPROVAL" if lint_res["passed"] else "REJECTED",
            rejection_reason=lint_res.get("reason")
        )
        self.drafts_store[draft_id] = draft
        return draft

    def approve_draft(self, draft_id: str, operator_name: str = "Admin") -> Dict[str, Any]:
        """Operator human-in-the-loop approval gate."""
        draft = self.drafts_store.get(draft_id)
        if not draft:
            return {"status": "ERROR", "message": "Draft not found"}
        if not draft.compliance_checks_passed:
            return {"status": "ERROR", "message": f"Cannot approve draft failing compliance: {draft.rejection_reason}"}
        
        draft.status = "APPROVED"
        return {
            "status": "APPROVED",
            "draft_id": draft_id,
            "approved_by": operator_name
        }

outreach_engine = OutreachEngine()
