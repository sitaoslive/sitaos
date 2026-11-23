"""
Alpha Vision AI Sales OS - Conversation Intelligence & Consultative Closer Engine
Classifies prospect responses, enforces immediate suppression on opt-outs, and handles objections truthfully.
"""
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from engine.compliance import compliance_gate

class ReplyClassification(BaseModel):
    intent: str  # INTERESTED, WANTS_DEMO, PRICING_INQUIRY, OBJECTION, UNSUBSCRIBE, COMPLAINT, ESCALATE_HUMAN, UNCLEAR
    confidence: float
    objection_type: Optional[str] = None
    recommended_action: str
    auto_suppressed: bool = False

class ConversationEngine:
    def __init__(self):
        self.conversation_threads: Dict[str, List[Dict[str, Any]]] = {}

    def classify_reply(self, message_text: str, prospect_email: Optional[str] = None) -> ReplyClassification:
        """Categorizes incoming prospect responses with deterministic intent filters."""
        text = message_text.lower().strip()

        # 1. Immediate Unsubscribe / Opt-Out Detection
        unsub_keywords = ["unsubscribe", "cancelar", "baja", "no me interesa", "no contactar", "stop", "quitar de la lista", "remove me"]
        if any(re.search(r'\b' + re.escape(w) + r'\b', text) for w in unsub_keywords):
            if prospect_email:
                compliance_gate.add_suppression("email", prospect_email, "prospect_unsubscribed", "conversation_classifier")
            return ReplyClassification(
                intent="UNSUBSCRIBE",
                confidence=0.99,
                recommended_action="STOP_ALL_OUTREACH",
                auto_suppressed=True
            )

        # 2. Urgent Human Escalation
        escalate_patterns = [
            "hablar con", "persona", "humano", "talk to human", "speak to a person", 
            "llámame", "llamada", "call me", "custom contract", "contrato empresarial", "enterprise"
        ]
        if any(w in text for w in escalate_patterns):
            return ReplyClassification(
                intent="ESCALATE_HUMAN",
                confidence=0.95,
                recommended_action="ROUTE_TO_HUMAN_OPERATOR",
                auto_suppressed=False
            )

        # 3. Demo Request / Acceptance
        if any(w in text for w in ["demo", "muéstrame", "show me", "ver demo", "send the link", "enlace", "probar", "test it", "cómo funciona"]):
            return ReplyClassification(
                intent="WANTS_DEMO",
                confidence=0.92,
                recommended_action="SEND_INTERACTIVE_DEMO_LINK",
                auto_suppressed=False
            )

        # 4. Pricing / Cost Inquiry
        if any(w in text for w in ["precio", "costo", "cuánto cuesta", "price", "how much", "plans", "planes", "tarifas"]):
            return ReplyClassification(
                intent="PRICING_INQUIRY",
                confidence=0.90,
                recommended_action="SEND_TRANSPARENT_PRICING_SUMMARY",
                auto_suppressed=False
            )

        # 5. Objection Detection
        objection_type = None
        if any(w in text for w in ["ya uso", "already have", "already use", "tenemos sistema", "usamos software"]):
            objection_type = "ALREADY_USE_SOFTWARE"
        elif any(w in text for w in ["caro", "expensive", "no presupuesto", "budget", "costoso"]):
            objection_type = "TOO_EXPENSIVE"
        elif any(w in text for w in ["difícil", "complicado", "no tengo tiempo", "no time", "too busy", "complicated"]):
            objection_type = "NO_TIME_FOR_IMPLEMENTATION"
        elif any(w in text for w in ["celular", "mobile", "funciona en móvil", "app", "iphone", "android"]):
            objection_type = "MOBILE_COMPATIBILITY"
        elif any(w in text for w in ["cancelar", "permanencia", "contrato forzoso", "lock-in"]):
            objection_type = "CANCELLATION_TERMS"

        if objection_type:
            return ReplyClassification(
                intent="OBJECTION",
                confidence=0.88,
                objection_type=objection_type,
                recommended_action="EXECUTE_GROUNDED_OBJECTION_PLAYBOOK",
                auto_suppressed=False
            )

        # 6. General Positive Interest
        if any(w in text for w in ["interesa", "interested", "cuéntame más", "tell me more", "de qué se trata", "sounds good", "me parece bien"]):
            return ReplyClassification(
                intent="INTERESTED",
                confidence=0.85,
                recommended_action="DISCOVER_CURRENT_SITUATION_AND_OFFER_DEMO",
                auto_suppressed=False
            )

        return ReplyClassification(
            intent="UNCLEAR",
            confidence=0.50,
            recommended_action="ASK_TARGETED_CLARIFICATION_QUESTION",
            auto_suppressed=False
        )

    def generate_consultative_response(self, objection_type: str, product_id: str, language: str = "es") -> str:
        """Provides verified, non-manipulative consultative responses grounded in actual capabilities."""
        if language == "es":
            if objection_type == "ALREADY_USE_SOFTWARE":
                return (
                    "Comprendo totalmente. Muchas clínicas y profesionales ya cuentan con algún software o usan hojas de cálculo y WhatsApp. "
                    "Nuestra plataforma no busca reemplazar de golpe lo que ya te funciona, sino resolver los cuellos de botella que suelen quedar "
                    "abiertos: el rastreo GPS en ruta de auxiliares, el conserje automatizado 24/7 y la emisión instantánea de fórmulas médicas sin digitación manual. "
                    "¿Te gustaría ver la demostración interactiva de 2 minutos para comparar cómo manejamos las visitas en ruta?"
                )
            elif objection_type == "TOO_EXPENSIVE":
                return (
                    "Es un punto completamente válido. Nuestros planes comienzan desde $189.000 COP/mes (o $49 USD) e incluyen 30 días de prueba gratuita "
                    "sin tarjeta de crédito para que compruebes si el ahorro de tiempo administrativo y la reducción de consultas perdidas justifican la inversión antes de pagar nada. "
                    "¿Quisieras activar el acceso de prueba y evaluarlo en tu práctica?"
                )
            elif objection_type == "NO_TIME_FOR_IMPLEMENTATION":
                return (
                    "Lo entiendo perfectamente: en el día a día no hay tiempo para aprender sistemas complicados. Por eso incluimos una sesión personal "
                    "de implementación de 45-60 minutos con nuestro equipo después de registrarte, donde dejamos configurados tus horarios, zonas y servicios por ti. "
                    "Además, la interfaz para celulares es tan sencilla que se opera con un par de toques."
                )
            elif objection_type == "MOBILE_COMPATIBILITY":
                return (
                    "Sí, funciona de forma nativa en cualquier celular (iPhone o Android) como Progressive Web App (PWA) sin necesidad de descargarla de tiendas. "
                    "Tus auxiliares o médicos pueden marcar llegada con GPS, cronometrar la consulta y emitir fórmulas directamente desde el teléfono."
                )
            elif objection_type == "CANCELLATION_TERMS":
                return (
                    "Cero permanencia ni cláusulas forzosas. La suscripción es mes a mes y puedes cancelar en cualquier momento con un clic. "
                    "Si decides no continuar, tus datos de pacientes y clientes se exportan íntegramente en formatos estándar."
                )
            else:
                return (
                    "Con gusto te explico los detalles. Nuestro objetivo es que conozcas exactamente las capacidades reales del sistema y decidas si "
                    "se adapta a tu forma de trabajo. ¿Qué aspecto de tu operación diaria te gustaría simplificar primero?"
                )
        else:
            # English Responses for Contractor / Trade OS
            if objection_type == "ALREADY_USE_SOFTWARE":
                return (
                    "Totally understand. Many trade businesses we speak with already use tools like Jobber, ServiceTitan, or QuickBooks. "
                    "We don't force you to rip everything out—our core strength is instant after-hours missed call capture via auto-SMS and our live field dispatch radar. "
                    "Would you be open to a quick 2-minute interactive demo to see how the customer journey flow compares?"
                )
            elif objection_type == "TOO_EXPENSIVE":
                return (
                    "Completely fair concern. Our Starter plan begins at $197/mo, and saving just a single missed $600 HVAC or plumbing emergency job covers the entire cost. "
                    "We also provide a 14-day zero-risk trial so you can evaluate real job scheduling before committing. Would you like to check out the plan breakdown?"
                )
            elif objection_type == "NO_TIME_FOR_IMPLEMENTATION":
                return (
                    "I hear you—contractors are in the field all day and don't have hours to configure complex software. That is why every plan includes a dedicated 1-on-1 "
                    "onboarding session with our team to configure your trade services, team schedule, and payment setup for you so you're ready to operate immediately."
                )
            elif objection_type == "MOBILE_COMPATIBILITY":
                return (
                    "100% mobile-friendly. Field technicians can punch in, pull up job checklists, log parts, and capture customer signatures directly on any smartphone or tablet."
                )
            elif objection_type == "CANCELLATION_TERMS":
                return (
                    "No long-term contracts or lock-in. You can cancel at any time, and you always retain full ownership and export access to all your client and job records."
                )
            else:
                return (
                    "Happy to clarify. Our goal is to make sure you have complete transparency into what the system can and cannot do. What is the biggest operational bottleneck you'd like to streamline?"
                )

conversation_engine = ConversationEngine()
