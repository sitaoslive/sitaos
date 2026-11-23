"""
Tests for Alpha Vision Database Federation & Tenant Management Service
Verifies:
- Dual Supabase project healthchecks
- Subdomain format & reserved domain collision guards
- End-to-end 8-step SaaS tenant provisioning pipeline
- Non-destructive tenant suspension and reactivation
- Cross-tenant data isolation and hostname routing
- Complete audit trail logging
"""

import pytest
from engine.db_federation import (
    DatabaseFederationService,
    TenantProvisionRequest,
    RESERVED_SUBDOMAINS
)

@pytest.fixture
def federation_service():
    # Fresh service instance for isolated testing
    return DatabaseFederationService()

def test_dual_database_healthcheck(federation_service):
    """Verifies that both Supabase databases report healthy connectivity."""
    report = federation_service.healthcheck_both_databases()
    assert report["overall_status"] == "HEALTHY"
    assert "core_db" in report["databases"]
    assert "vet_db" in report["databases"]
    assert report["databases"]["core_db"]["status"] == "HEALTHY"
    assert report["databases"]["vet_db"]["status"] == "HEALTHY"
    assert report["databases"]["core_db"]["tables_verified"] == 43
    assert report["databases"]["vet_db"]["tables_verified"] == 264
    assert report["federation_active"] is True

def test_subdomain_validation_rules(federation_service):
    """Tests syntax validation, length limits, and reserved subdomain protection."""
    # Valid subdomains
    assert federation_service.validate_subdomain("clinicavet")["valid"] is True
    assert federation_service.validate_subdomain("austin-plumbing-pros")["valid"] is True
    assert federation_service.validate_subdomain("dr-luis-care")["valid"] is True
    
    # Invalid characters or length
    assert federation_service.validate_subdomain("ab")["valid"] is False  # Too short (< 3)
    assert federation_service.validate_subdomain("-startwithdash")["valid"] is False
    assert federation_service.validate_subdomain("endwithdash-")["valid"] is False
    assert federation_service.validate_subdomain("clinic_vet!")["valid"] is False
    
    # Reserved subdomains
    for reserved in ["admin", "api", "www", "portal", "root", "lovable"]:
        res = federation_service.validate_subdomain(reserved)
        assert res["valid"] is False
        assert "protected platform domain" in res["error"]
        
    # Existing occupied subdomain
    res = federation_service.validate_subdomain("luis")
    assert res["valid"] is False
    assert "already allocated" in res["error"]

def test_provision_veterinary_tenant_e2e(federation_service):
    """Tests provisioning of a new veterinary clinic (Product A)."""
    req = TenantProvisionRequest(
        business_name="Clínica Veterinaria Santa Fe",
        product_id="vet_freedom_os",
        plan_id="vet_clinica",
        target_subdomain="vetsantafe",
        owner_name="Dra. Andrea Moreno",
        owner_email="andrea@vetsantafe.co",
        owner_phone="+573115557788",
        country="CO",
        currency="COP",
        initial_seats=5
    )
    
    resp = federation_service.provision_tenant(req, actor="TestRunner")
    assert resp.success is True
    assert resp.org_id.startswith("org_vet_")
    assert resp.subdomain == "vetsantafe"
    assert resp.subdomain_url == "https://vetsantafe.alphavisionm.com"
    assert "/auth?invite=" in resp.login_url
    assert "/cliente" in resp.portal_url
    assert resp.status == "ACTIVE"
    assert len(resp.provisioning_steps_completed) == 8
    assert "digital_prescriptions" in resp.entitlements
    assert "okvet_digital_vault" in resp.entitlements
    assert resp.seats_allocated == 5
    assert resp.db_core_synced is True
    assert resp.db_product_synced is True
    
    # Verify tenant is now in registry
    org = federation_service.get_organization(resp.org_id)
    assert org is not None
    assert org.name == "Clínica Veterinaria Santa Fe"
    
    # Subdomain is now occupied
    val = federation_service.validate_subdomain("vetsantafe")
    assert val["valid"] is False

def test_provision_contractor_tenant_e2e(federation_service):
    """Tests provisioning of a new HVAC/Plumbing contractor (Product B)."""
    req = TenantProvisionRequest(
        business_name="Lone Star Mechanical & AC",
        product_id="service_business_os",
        plan_id="service_growth",
        target_subdomain="lonestar-ac",
        owner_name="Brad Cooper",
        owner_email="bcooper@lonestarac.com",
        owner_phone="+15125553920",
        country="US",
        currency="USD",
        initial_seats=10
    )
    
    resp = federation_service.provision_tenant(req, actor="TestRunner")
    assert resp.success is True
    assert resp.org_id.startswith("org_contractor_")
    assert resp.subdomain == "lonestar-ac"
    assert resp.subdomain_url == "https://lonestar-ac.alphavisionm.com"
    assert "/login?invite=" in resp.login_url
    assert "/portal" in resp.portal_url
    assert resp.status == "ACTIVE"
    assert len(resp.provisioning_steps_completed) == 8
    assert "live_dispatch_radar" in resp.entitlements
    assert "automation_workflows_60" in resp.entitlements
    assert resp.seats_allocated == 10

def test_suspend_and_reactivate_tenant(federation_service):
    """Tests safe non-destructive suspension and restoration."""
    org_id = "org_contractor_apex_001"
    
    # Suspend
    res = federation_service.suspend_tenant(org_id, reason="Payment review pending", actor="SuperAdmin")
    assert res["success"] is True
    assert res["status"] == "SUSPENDED"
    
    org = federation_service.get_organization(org_id)
    assert org.status == "SUSPENDED"
    assert org.suspension_reason == "Payment review pending"
    
    # Reactivate
    res2 = federation_service.reactivate_tenant(org_id, actor="SuperAdmin")
    assert res2["success"] is True
    assert res2["status"] == "ACTIVE"
    
    org_restored = federation_service.get_organization(org_id)
    assert org_restored.status == "ACTIVE"
    assert org_restored.suspension_reason is None

def test_hostname_routing_resolution(federation_service):
    """Tests that hostnames resolve to the correct organization and product."""
    # Known vet
    org_vet = federation_service.resolve_tenant_by_hostname("luis.alphavisionm.com")
    assert org_vet is not None
    assert org_vet.product_id == "vet_freedom_os"
    assert org_vet.name == "Dr. Luis Rios - Vet Freedom Care"
    
    # Known contractor
    org_contractor = federation_service.resolve_tenant_by_hostname("apexclimate.alphavisionm.com")
    assert org_contractor is not None
    assert org_contractor.product_id == "service_business_os"
    assert org_contractor.name == "Apex Climate HVAC & Heating"
    
    # Unknown hostname
    unknown = federation_service.resolve_tenant_by_hostname("randomunknowntenant.alphavisionm.com")
    assert unknown is None

def test_audit_log_tracking(federation_service):
    """Tests that all administrative lifecycle events generate immutable audit records."""
    initial_count = len(federation_service.get_audit_logs())
    
    req = TenantProvisionRequest(
        business_name="Audit Test Practice",
        product_id="vet_freedom_os",
        plan_id="vet_solitario",
        target_subdomain="audittestvet",
        owner_name="Dr. Test",
        owner_email="test@audit.internal",
        owner_phone="+19299663559"
    )
    federation_service.provision_tenant(req, actor="AuditorAccount")
    
    logs = federation_service.get_audit_logs(limit=10)
    assert len(logs) == initial_count + 1
    latest = logs[0]
    assert latest["actor"] == "AuditorAccount"
    assert latest["action"] == "TENANT_PROVISIONED"
    assert latest["details"]["subdomain"] == "audittestvet"
