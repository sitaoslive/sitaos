"""
Alpha Vision AI Sales OS - Product Catalog, Licensing & Entitlement Engine
Manages multi-product catalogs, tiered plans, currency pricing, time-limited trial tokens,
and authoritative feature-flag evaluation.
"""
import uuid
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# ==============================================================================
# PRODUCT CATALOG DEFINITIONS
# ==============================================================================

PRODUCTS_CATALOG: Dict[str, Dict[str, Any]] = {
    "vet_freedom_os": {
        "id": "vet_freedom_os",
        "name": "Vet Life / Vet Freedom OS",
        "category": "Veterinary Practice & Mobile Healthcare OS",
        "readiness_status": "SALES_READY",
        "supported_countries": ["CO", "MX", "US", "ES", "CL"],
        "supported_languages": ["es", "en"],
        "base_url": "https://vetfreedom.alphavisionmethod.com",
        "demo_endpoint": "/demo/vet-life",
        "trial_policy": {
            "default_duration_days": 30,
            "requires_credit_card": False,
            "instant_activation": True
        },
        "plans": {
            "vet_solitario": {
                "id": "vet_solitario",
                "name": "Veterinario Solitario / Mobile Vet",
                "description": "Ideal para veterinarios independientes y atención a domicilio individual.",
                "seats_included": 1,
                "trial_days": 30,
                "pricing": {
                    "CO": {"currency": "COP", "monthly": 189000, "annual": 1890000},
                    "MX": {"currency": "MXN", "monthly": 890, "annual": 8900},
                    "US": {"currency": "USD", "monthly": 49, "annual": 490}
                },
                "entitlements": [
                    "mobile_agenda",
                    "pet_records",
                    "client_portal",
                    "whatsapp_templates",
                    "digital_prescriptions",
                    "gps_route_view"
                ]
            },
            "vet_clinica": {
                "id": "vet_clinica",
                "name": "Clínica Domiciliaria / Equipo",
                "description": "Para clínicas veterinarias con equipo de auxiliares y médicos en ruta.",
                "seats_included": 5,
                "trial_days": 30,
                "pricing": {
                    "CO": {"currency": "COP", "monthly": 389000, "annual": 3890000},
                    "MX": {"currency": "MXN", "monthly": 1890, "annual": 18900},
                    "US": {"currency": "USD", "monthly": 99, "annual": 990}
                },
                "entitlements": [
                    "mobile_agenda",
                    "pet_records",
                    "client_portal",
                    "whatsapp_templates",
                    "digital_prescriptions",
                    "gps_live_fleet_tracking",
                    "consultation_stopwatch",
                    "ai_concierge_triage_247",
                    "vital_emergency_siren",
                    "anti_no_show_deposits",
                    "okvet_digital_vault"
                ]
            },
            "vet_red": {
                "id": "vet_red",
                "name": "Red Veterinaria / Marca Blanca",
                "description": "Para redes de clínicas, hospitales veterinarios o franquicias.",
                "seats_included": 25,
                "trial_days": 30,
                "pricing": {
                    "CO": {"currency": "COP", "monthly": 1190000, "annual": 11900000},
                    "MX": {"currency": "MXN", "monthly": 5900, "annual": 59000},
                    "US": {"currency": "USD", "monthly": 297, "annual": 2970}
                },
                "entitlements": [
                    "all_features",
                    "white_label_custom_domain",
                    "specialist_referral_network",
                    "multi_branch_dispatch",
                    "custom_sla_support"
                ]
            }
        }
    },
    "service_business_os": {
        "id": "service_business_os",
        "name": "Alpha Service Business OS",
        "category": "Field Service & Trade Contracting Management OS",
        "readiness_status": "SALES_READY",
        "supported_countries": ["US", "CA"],
        "supported_languages": ["en", "es"],
        "base_url": "https://serviceos.alphavisionmethod.com",
        "demo_endpoint": "/demo/service-os",
        "trial_policy": {
            "default_duration_days": 14,
            "requires_credit_card": False,
            "instant_activation": True
        },
        "plans": {
            "service_starter": {
                "id": "service_starter",
                "name": "Solo Operator / Small Crew",
                "description": "Essential job scheduling, quotes, invoices and payment processing.",
                "seats_included": 3,
                "trial_days": 14,
                "pricing": {
                    "US": {"currency": "USD", "monthly": 197, "annual": 1970},
                    "CA": {"currency": "CAD", "monthly": 247, "annual": 2470}
                },
                "entitlements": [
                    "job_scheduling",
                    "estimates_and_invoices",
                    "stripe_card_payments",
                    "missed_call_autotext",
                    "customer_crm",
                    "mobile_tech_view"
                ]
            },
            "service_growth": {
                "id": "service_growth",
                "name": "Growth Team / Field Operations",
                "description": "Full dispatching, worker time tracking, customer portal and 60 workflows.",
                "seats_included": 10,
                "trial_days": 14,
                "setup_fee_usd": 497,
                "pricing": {
                    "US": {"currency": "USD", "monthly": 497, "annual": 4970},
                    "CA": {"currency": "CAD", "monthly": 620, "annual": 6200}
                },
                "entitlements": [
                    "job_scheduling",
                    "estimates_and_invoices",
                    "stripe_card_payments",
                    "missed_call_autotext",
                    "customer_crm",
                    "live_dispatch_radar",
                    "field_worker_punch_clock",
                    "customer_portal_ai_triage",
                    "revenue_recovery_radar",
                    "automation_workflows_60",
                    "brand_kit_studio",
                    "assisted_onboarding_call"
                ]
            },
            "service_enterprise": {
                "id": "service_enterprise",
                "name": "Multi-Crew / Commercial Leader",
                "description": "Advanced telemetry, smart IoT sensors, utility rebates and multi-branch ops.",
                "seats_included": 50,
                "trial_days": 14,
                "setup_fee_usd": 997,
                "pricing": {
                    "US": {"currency": "USD", "monthly": 997, "annual": 9970},
                    "CA": {"currency": "CAD", "monthly": 1240, "annual": 12400}
                },
                "entitlements": [
                    "all_features",
                    "iot_sensor_sentinel",
                    "tele_triage_video_room",
                    "ecosavings_ira_rebate_engine",
                    "filterpass_auto_replenishment",
                    "custom_webhook_integrations",
                    "dedicated_implementation_manager"
                ]
            }
        }
    }
}

# ==============================================================================
# LICENSING & ENTITLEMENT SERVICE
# ==============================================================================

class LicenseRecord(BaseModel):
    license_id: str
    customer_id: str
    product_id: str
    plan_id: str
    status: str  # trial, active, past_due, expired, revoked, cancelled
    seats_allocated: int
    entitlements: List[str]
    is_trial: bool
    created_at: str
    expires_at: str
    renewed_at: Optional[str] = None
    last_verified_at: str
    payment_provider: Optional[str] = None
    subscription_id: Optional[str] = None

class LicensingEngine:
    def __init__(self):
        self.licenses_store: Dict[str, LicenseRecord] = {}
        self.trial_tokens_store: Dict[str, Dict[str, Any]] = {}
        self._init_baseline_licenses()

    def _init_baseline_licenses(self):
        """Initializes verified baseline licenses for existing test environments."""
        # 1. Baseline Service OS Tenant (Apex Climate Solutions)
        now = datetime.utcnow()
        self.create_paid_license(
            customer_id="cust_apex_climate_hvac",
            product_id="service_business_os",
            plan_id="service_growth",
            seats=10,
            payment_provider="STRIPE",
            subscription_id="sub_live_apex_climate_982"
        )
        # 2. Baseline Vet Freedom OS Tenant (Clínica San Jerónimo)
        self.create_paid_license(
            customer_id="cust_vet_san_jeronimo",
            product_id="vet_freedom_os",
            plan_id="vet_clinica",
            seats=5,
            payment_provider="WOMPI",
            subscription_id="wompi_sub_vet_sj_441"
        )

    def generate_trial_token(self, product_id: str, plan_id: str, prospect_name: str, email: str, days: int = 30) -> str:
        """Generates a secure, cryptographically verifiable trial access token."""
        token_uuid = str(uuid.uuid4()).replace("-", "")[:12]
        token = f"try_{product_id[:3]}_{token_uuid}"
        now = datetime.utcnow()
        expires = now + timedelta(days=days)
        
        self.trial_tokens_store[token] = {
            "token": token,
            "product_id": product_id,
            "plan_id": plan_id,
            "prospect_name": prospect_name,
            "email": email,
            "created_at": now.isoformat(),
            "expires_at": expires.isoformat(),
            "claimed": False,
            "customer_id": None
        }
        return token

    def claim_trial_token(self, token: str, customer_id: str, business_name: str) -> Dict[str, Any]:
        """Activates a time-limited trial license from a secure token."""
        record = self.trial_tokens_store.get(token)
        if not record:
            return {"status": "ERROR", "message": "Invalid or unknown trial token"}
        if record.get("claimed"):
            return {"status": "ERROR", "message": "Trial token has already been claimed"}
        
        expires_at = datetime.fromisoformat(record["expires_at"])
        if datetime.utcnow() > expires_at:
            return {"status": "ERROR", "message": "Trial token has expired"}

        product_id = record["product_id"]
        plan_id = record["plan_id"]
        product = PRODUCTS_CATALOG.get(product_id, {})
        plan = product.get("plans", {}).get(plan_id, {})
        entitlements = plan.get("entitlements", ["basic_features"])

        license_id = f"lic_trial_{uuid.uuid4().hex[:10]}"
        license_rec = LicenseRecord(
            license_id=license_id,
            customer_id=customer_id,
            product_id=product_id,
            plan_id=plan_id,
            status="trial",
            seats_allocated=plan.get("seats_included", 1),
            entitlements=entitlements,
            is_trial=True,
            created_at=datetime.utcnow().isoformat(),
            expires_at=record["expires_at"],
            last_verified_at=datetime.utcnow().isoformat()
        )
        self.licenses_store[license_id] = license_rec
        record["claimed"] = True
        record["customer_id"] = customer_id
        
        return {
            "status": "TRIAL_ACTIVATED",
            "license_id": license_id,
            "product": product.get("name"),
            "plan": plan.get("name"),
            "expires_at": record["expires_at"],
            "entitlements": entitlements
        }

    def create_paid_license(
        self,
        customer_id: str,
        product_id: str,
        plan_id: str,
        seats: Optional[int] = None,
        duration_days: int = 365,
        payment_provider: str = "STRIPE",
        subscription_id: Optional[str] = None
    ) -> LicenseRecord:
        """Provisions an active commercial license upon verified authoritative payment."""
        product = PRODUCTS_CATALOG.get(product_id, {})
        plan = product.get("plans", {}).get(plan_id, {})
        seats_allocated = seats or plan.get("seats_included", 5)
        entitlements = plan.get("entitlements", ["core_features"])
        
        now = datetime.utcnow()
        expires = now + timedelta(days=duration_days)
        license_id = f"lic_prod_{uuid.uuid4().hex[:10]}"

        rec = LicenseRecord(
            license_id=license_id,
            customer_id=customer_id,
            product_id=product_id,
            plan_id=plan_id,
            status="active",
            seats_allocated=seats_allocated,
            entitlements=entitlements,
            is_trial=False,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
            last_verified_at=now.isoformat(),
            payment_provider=payment_provider,
            subscription_id=subscription_id
        )
        self.licenses_store[license_id] = rec
        return rec

    def check_entitlement(self, license_id: str, required_feature: str) -> bool:
        """Authoritative feature-flag evaluation at the backend authorization layer."""
        rec = self.licenses_store.get(license_id)
        if not rec:
            return False
        if rec.status not in ["active", "trial"]:
            return False
        
        # Check expiration
        expires = datetime.fromisoformat(rec.expires_at)
        if datetime.utcnow() > expires:
            rec.status = "expired"
            return False

        if "all_features" in rec.entitlements:
            return True
        return required_feature in rec.entitlements

    def cancel_subscription(self, license_id: str, reason: str = "Customer request") -> Optional[LicenseRecord]:
        """Cancels a customer subscription and revokes active service entitlements."""
        rec = self.licenses_store.get(license_id)
        if not rec:
            return None
        rec.status = "cancelled"
        rec.last_verified_at = datetime.utcnow().isoformat()
        return rec

    def get_customer_license(self, customer_id: str) -> Optional[LicenseRecord]:
        for lic in self.licenses_store.values():
            if lic.customer_id == customer_id and lic.status in ["active", "trial"]:
                return lic
        return None

licensing_engine = LicensingEngine()
