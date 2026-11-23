"""
Alpha Vision Revenue OS - Approved WhatsApp Templates Catalog
Pre-configured, Meta-compliant templates for utility notifications, demo access,
license delivery, and onboarding call reminders in Spanish and English.
"""

from typing import Dict, Any, List, Optional

APPROVED_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "avm_onboarding_reminder_v1": {
        "name": "avm_onboarding_reminder_v1",
        "category": "UTILITY",
        "languages": ["es", "en"],
        "description": "Onboarding session reminder for post-purchase 1-on-1 implementation call.",
        "parameters": ["customer_name", "date_formatted", "time_formatted", "meeting_link"],
        "template_es": (
            "Hola {{1}}, te recordamos tu sesión de Onboarding e Implementación personalizada "
            "con Alpha Vision el {{2}} a las {{3}}. "
            "Enlace de reunión: {{4}}.\n"
            "Responde a este mensaje si necesitas reprogramar."
        ),
        "template_en": (
            "Hi {{1}}, this is a reminder for your 1-on-1 Onboarding & Implementation session "
            "with Alpha Vision on {{2}} at {{3}}. "
            "Join link: {{4}}.\n"
            "Reply to this message if you need to reschedule."
        )
    },
    "avm_demo_access_v1": {
        "name": "avm_demo_access_v1",
        "category": "UTILITY",
        "languages": ["es", "en"],
        "description": "Interactive SaaS product demonstration access delivery.",
        "parameters": ["customer_name", "product_name", "demo_url"],
        "template_es": (
            "Hola {{1}}, tu demostración interactiva de {{2}} está lista. "
            "Puedes acceder con tu entorno personalizado aquí: {{3}}.\n"
            "Tu acceso estará activo durante 48 horas."
        ),
        "template_en": (
            "Hi {{1}}, your interactive demo for {{2}} is ready. "
            "Access your personalized environment here: {{3}}.\n"
            "Your access is active for 48 hours."
        )
    },
    "avm_license_activated_v1": {
        "name": "avm_license_activated_v1",
        "category": "UTILITY",
        "languages": ["es", "en"],
        "description": "Commercial license provisioning confirmation and admin portal link.",
        "parameters": ["customer_name", "product_name", "login_url"],
        "template_es": (
            "¡Felicidades {{1}}! Tu suscripción a {{2}} ha sido provisionada exitosamente. "
            "Accede a tu panel de control aquí: {{3}}.\n"
            "Tu especialista de implementación te contactará para tu llamada de configuración."
        ),
        "template_en": (
            "Congratulations {{1}}! Your subscription to {{2}} is now active. "
            "Access your management dashboard here: {{3}}.\n"
            "Your onboarding specialist will assist you during your setup call."
        )
    },
    "avm_sales_followup_v1": {
        "name": "avm_sales_followup_v1",
        "category": "MARKETING",
        "languages": ["es", "en"],
        "description": "Opted-in prospective buyer follow-up.",
        "parameters": ["prospect_name", "company_name", "asset_link"],
        "template_es": (
            "Hola {{1}}, preparamos un análisis de automatización para {{2}}. "
            "Puedes consultar los detalles aquí: {{3}}.\n"
            "Escribe PARAR si no deseas recibir más actualizaciones."
        ),
        "template_en": (
            "Hi {{1}}, we prepared an automation overview for {{2}}. "
            "You can review it here: {{3}}.\n"
            "Reply STOP to unsubscribe from future updates."
        )
    }
}

class WhatsAppTemplateEngine:
    """Prepares and validates template components for Meta Cloud API dispatch."""

    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        return APPROVED_TEMPLATES.get(template_name)

    def build_components(self, template_name: str, parameters: List[str]) -> List[Dict[str, Any]]:
        """Constructs Meta Graph API format parameters component."""
        params = [{"type": "text", "text": str(p)} for p in parameters]
        return [
            {
                "type": "body",
                "parameters": params
            }
        ]

whatsapp_templates = WhatsAppTemplateEngine()
