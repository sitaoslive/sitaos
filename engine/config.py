"""
Alpha Vision AI Sales OS - Global Production Configuration
"""
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# Load .env file automatically
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    with open(_env_path, "r", encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

class SalesOSConfig(BaseModel):
    # System Identity & Environment
    SYSTEM_NAME: str = "Alpha Vision AI Sales OS"
    SYSTEM_VERSION: str = "2.5.0"
    ENVIRONMENT: str = os.getenv("SALES_OS_ENV", "production")
    
    # Financial Targets
    TARGET_MONTHLY_NET_PROFIT_USD: float = 50000.0
    MIN_GROSS_MARGIN_PCT: float = 85.0
    MAX_CAC_PAYBACK_MONTHS: int = 3
    MAX_AI_COST_PER_PROSPECT_USD: float = 0.05
    MAX_AI_COST_PER_CONVERSATION_USD: float = 0.15
    
    # AI Cognitive Reasoning Layer (Claude API)
    ANTHROPIC_API_KEY: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    CLAUDE_MODEL_DEEP_REASONING: str = os.getenv("CLAUDE_MODEL_DEEP_REASONING", "claude-3-5-sonnet-20241022")
    CLAUDE_MODEL_FAST_TRIAGE: str = os.getenv("CLAUDE_MODEL_FAST_TRIAGE", "claude-3-5-haiku-20241022")
    
    # CRM & Commercial Hub (GoHighLevel)
    GHL_API_KEY: str = Field(default_factory=lambda: os.getenv("GHL_API_KEY", ""))
    GHL_LOCATION_ID: str = Field(default_factory=lambda: os.getenv("GHL_LOCATION_ID", ""))
    GHL_BASE_URL: str = os.getenv("GHL_BASE_URL", "https://services.leadconnectorhq.com")
    GHL_CALENDAR_ONBOARDING_ID: str = os.getenv("GHL_CALENDAR_ONBOARDING_ID", "cal_avm_onboarding_master")
    GHL_CALENDAR_CLARITY_ID: str = os.getenv("GHL_CALENDAR_CLARITY_ID", "2Btd7kd9NkVtIWA9glW4")
    
    # Database Layer (Supabase PostgreSQL)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://djtejmrzxfkctbvpdkbg.supabase.co")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default_factory=lambda: os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""))
    
    # Automation Layer (n8n Cloud)
    N8N_BASE_URL: str = os.getenv("N8N_BASE_URL", "https://alphavision.app.n8n.cloud")
    N8N_LOCAL_WEBHOOK_URL: str = os.getenv("N8N_LOCAL_WEBHOOK_URL", "http://localhost:5678/webhook")
    N8N_API_KEY: str = Field(default_factory=lambda: os.getenv("N8N_API_KEY", ""))
    
    # Payment Gateways
    STRIPE_SECRET_KEY: str = Field(default_factory=lambda: os.getenv("STRIPE_SECRET_KEY", ""))
    STRIPE_WEBHOOK_SECRET: str = Field(default_factory=lambda: os.getenv("STRIPE_WEBHOOK_SECRET", ""))
    WOMPI_PUBLIC_KEY: str = Field(default_factory=lambda: os.getenv("WOMPI_PUBLIC_KEY", ""))
    WOMPI_PRIVATE_KEY: str = Field(default_factory=lambda: os.getenv("WOMPI_PRIVATE_KEY", ""))
    MERCADOPAGO_ACCESS_TOKEN: str = Field(default_factory=lambda: os.getenv("MERCADOPAGO_ACCESS_TOKEN", ""))
    
    # Outbound Delivery (Smartlead & WhatsApp Cloud API)
    SMARTLEAD_API_KEY: str = Field(default_factory=lambda: os.getenv("SMARTLEAD_API_KEY", ""))
    WHATSAPP_TOKEN: str = Field(default_factory=lambda: os.getenv("WHATSAPP_TOKEN", ""))
    WHATSAPP_PHONE_NUMBER_ID: str = Field(default_factory=lambda: os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""))
    META_APP_ID: str = Field(default_factory=lambda: os.getenv("META_APP_ID", ""))
    META_APP_SECRET: str = Field(default_factory=lambda: os.getenv("META_APP_SECRET", ""))
    META_WABA_ID: str = Field(default_factory=lambda: os.getenv("META_WABA_ID", ""))
    META_PHONE_NUMBER_ID: str = Field(default_factory=lambda: os.getenv("META_PHONE_NUMBER_ID", os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")))
    META_ACCESS_TOKEN: str = Field(default_factory=lambda: os.getenv("META_ACCESS_TOKEN", os.getenv("WHATSAPP_TOKEN", "")))
    META_WEBHOOK_VERIFY_TOKEN: str = Field(default_factory=lambda: os.getenv("META_WEBHOOK_VERIFY_TOKEN", "alpha_vision_meta_wa_2026_webhook_verify"))
    
    # GHL WhatsApp Custom Field IDs
    GHL_FIELD_WA_WINDOW: str = "ZG4CF1R3JMBooz9vAz6R"
    GHL_FIELD_WA_LAST_MSG: str = "0x5nGLlXI6VRRoblU3my"
    GHL_FIELD_WA_STATE: str = "k0C3j0lxNj8cVdoFfvmg"
    GHL_FIELD_WA_CONSENT: str = "XhgrU1U4iWY5M6cWrRic"
    
    # Commercial Sending Limits & Guardrails
    MAX_OUTREACH_PER_DAY: int = 100
    MAX_FOLLOWUPS_PER_CONTACT: int = 3
    TCPA_QUIET_HOURS_START: int = 20  # 8:00 PM local
    TCPA_QUIET_HOURS_END: int = 8    # 8:00 AM local
    KILL_SWITCH_ACTIVE: bool = False

config = SalesOSConfig()
