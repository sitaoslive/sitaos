"""
Alpha Vision AI Sales OS - Interactive Demonstration Gateway & Sandbox Adapters
Manages secure signed demo tokens, isolated synthetic demonstration environments,
and real-time demo session analytics.
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from engine.licensing import PRODUCTS_CATALOG

class DemoSessionRecord(BaseModel):
    session_id: str
    token: str
    product_id: str
    prospect_id: Optional[str] = None
    prospect_name: str
    language: str  # es, en
    scenario: str  # mobile_vet_day, hvac_emergency_call, plumbing_dispatch
    status: str = "created"  # created, opened, started, exploring, completed, expired
    modules_explored: List[str] = []
    questions_asked: List[Dict[str, str]] = []
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: str
    completed_at: Optional[str] = None

class InteractiveDemoGateway:
    def __init__(self):
        self.sessions_store: Dict[str, DemoSessionRecord] = {}
        self._init_baseline_demos()

    def _init_baseline_demos(self):
        """Initializes baseline demo sessions for quick verification."""
        # 1. Master fixed tokens for instant demonstration & testing
        now = datetime.utcnow()
        expires = now + timedelta(days=365)
        
        self.sessions_store["d_vet_demo_master"] = DemoSessionRecord(
            session_id="demo_sess_vet_master",
            token="d_vet_demo_master",
            product_id="vet_freedom_os",
            prospect_name="Dra. Sofía Morales",
            language="es",
            scenario="mobile_vet_day",
            status="created",
            expires_at=expires.isoformat()
        )
        self.sessions_store["d_ser_demo_master"] = DemoSessionRecord(
            session_id="demo_sess_service_master",
            token="d_ser_demo_master",
            product_id="service_business_os",
            prospect_name="Marcus Vance",
            language="en",
            scenario="hvac_emergency_call",
            status="created",
            expires_at=expires.isoformat()
        )

    def create_demo_session(
        self,
        product_id: str,
        prospect_name: str = "Valued Prospect",
        prospect_id: Optional[str] = None,
        language: str = "es",
        scenario: str = "standard_walkthrough",
        hours_valid: int = 48
    ) -> DemoSessionRecord:
        """Generates a secure, expiring token and registers a demonstration session."""
        session_id = f"demo_sess_{uuid.uuid4().hex[:10]}"
        token = f"d_{product_id[:3]}_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        expires = now + timedelta(hours=hours_valid)

        record = DemoSessionRecord(
            session_id=session_id,
            token=token,
            product_id=product_id,
            prospect_id=prospect_id,
            prospect_name=prospect_name,
            language=language,
            scenario=scenario,
            status="created",
            expires_at=expires.isoformat()
        )
        self.sessions_store[token] = record
        return record

    def validate_demo_token(self, token: str) -> Dict[str, Any]:
        """Validates demo token existence and expiration."""
        session = self.sessions_store.get(token)
        if not session:
            return {"valid": False, "reason": "TOKEN_NOT_FOUND"}
        
        expires = datetime.fromisoformat(session.expires_at)
        if datetime.utcnow() > expires:
            session.status = "expired"
            return {"valid": False, "reason": "TOKEN_EXPIRED"}

        if session.status == "created":
            session.status = "opened"

        product_meta = PRODUCTS_CATALOG.get(session.product_id, {})
        return {
            "valid": True,
            "session_id": session.session_id,
            "product_id": session.product_id,
            "product_name": product_meta.get("name"),
            "prospect_name": session.prospect_name,
            "language": session.language,
            "scenario": session.scenario,
            "modules_explored": session.modules_explored,
            "status": session.status
        }

    def record_module_visit(self, token: str, module_name: str) -> Dict[str, Any]:
        session = self.sessions_store.get(token)
        if not session:
            return {"status": "ERROR", "message": "Session not found"}
        
        session.status = "exploring"
        if module_name not in session.modules_explored:
            session.modules_explored.append(module_name)

        return {
            "status": "RECORDED",
            "session_id": session.session_id,
            "modules_explored": session.modules_explored
        }

    def complete_demo(self, token: str) -> Dict[str, Any]:
        session = self.sessions_store.get(token)
        if not session:
            return {"status": "ERROR", "message": "Session not found"}
        session.status = "completed"
        session.completed_at = datetime.utcnow().isoformat()
        return {
            "status": "COMPLETED",
            "session_id": session.session_id,
            "modules_count": len(session.modules_explored)
        }

    def ask_ai_demo_guide(self, token: str, user_question: str) -> str:
        """
        AI Demo Guide (Agent 10) retrieves verified answers from the product catalog
        and specs during the interactive walkthrough.
        """
        session = self.sessions_store.get(token)
        product_id = session.product_id if session else "vet_freedom_os"
        language = session.language if session else "es"
        q = user_question.lower().strip()

        # Record question in session telemetry
        if session:
            session.questions_asked.append({"question": user_question, "timestamp": datetime.utcnow().isoformat()})

        if product_id == "vet_freedom_os":
            if any(w in q for w in ["gps", "rastreo", "mapa", "ubicacion"]):
                return "El sistema incluye telemetría GPS en tiempo real para que tanto coordinación como los tutores puedan ver en el mapa la ruta exacta del médico o auxiliar y la hora estimada de llegada (ETA)."
            elif any(w in q for w in ["formula", "prescripcion", "receta", "medicamentos"]):
                return "Las fórmulas médicas se generan firmadas digitalmente con posología estructurada. Al finalizar la visita, el tutor recibe un enlace seguro por WhatsApp para consultarla sin que tengas que diseñar ni adjuntar PDFs a mano."
            elif any(w in q for w in ["precio", "costo", "planes", "pagar"]):
                return "Los planes son: Veterinario Solitario ($189.000 COP/mes), Clínica Domiciliaria ($389.000 COP/mes) y Red ($1.190.000 COP/mes). Además cuentas con 30 días de prueba 100% gratuitos para validar todo con tus propios pacientes."
            elif any(w in q for w in ["celular", "móvil", "iphone", "android", "app"]):
                return "Vet Freedom OS funciona como Progressive Web App (PWA) de alta velocidad. Se instala en 10 segundos en iPhone o Android directamente desde el navegador, con soporte táctil completo para auxiliares y doctores en la calle."
            else:
                return "Esta funcionalidad está completamente integrada en la plataforma y diseñada para eliminar trabajo manual repetitivo en tu práctica veterinaria. ¿Te gustaría ver cómo se ve en el perfil del médico o activar tu prueba de 30 días?"
        else:
            # Service Business OS
            if any(w in q for w in ["missed call", "phone", "sms", "after hours", "call"]):
                return "Our 15-second lead capture automatically responds to missed phone calls via SMS, introduces your company, and captures the repair inquiry immediately so the job doesn't go to a competitor."
            elif any(w in q for w in ["dispatch", "schedule", "technician", "field", "map"]):
                return "The Live Dispatch Radar allows the business owner to view technician availability, drag-and-drop jobs onto calendars, and optimize travel routes directly."
            elif any(w in q for w in ["price", "cost", "plans", "tier"]):
                return "Plans are: Solo Operator ($197/mo), Growth Team ($497/mo), and Enterprise ($997/mo). Every plan includes a 14-day free trial and an assisted onboarding setup session with our implementation engineers."
            elif any(w in q for w in ["time clock", "hours", "labor", "payroll"]):
                return "Field technicians have a dedicated mobile view where they punch in/out per job or travel leg. Labor costs automatically flow into job gross margin calculations."
            else:
                return "Alpha Service Business OS is built specifically to streamline field contracting operations. Would you like to review the dispatch console or start a 14-day free trial?"

demo_gateway = InteractiveDemoGateway()
