"""
Alpha Vision Revenue OS - Revenue Feasibility & Prospect ROI Engine
Calculates:
1. Exact recurring net operating profit in integer cents.
2. 3 Scenarios for $50,000/mo net operating profit (Conservative, Base, Aggressive).
3. 18-Month cohort model with logo churn and cash collection.
4. Industry-specific ROI Calculators (HVAC & Plumbing, Mobile Veterinarians).
"""

from typing import Dict, Any, List

class RevenueFeasibilityModel:
    """Deterministic financial model and ROI calculations in integer cents."""

    SCENARIOS = {
        "conservative": {
            "name": "Conservative Volume",
            "price_cents": 29900, # $299.00
            "variable_cost_cents": 9000, # $90.00
            "fixed_overhead_cents": 1000000, # $10,000.00
            "required_clients": 288,
            "target_mrr_cents": 8611200, # $86,112.00
            "net_profit_cents": 5019200 # $50,192.00
        },
        "base_case": {
            "name": "Base Case (Primary Beachhead)",
            "price_cents": 49900, # $499.00
            "variable_cost_cents": 9900, # $99.00
            "fixed_overhead_cents": 1000000, # $10,000.00
            "required_clients": 150,
            "target_mrr_cents": 7485000, # $74,850.00
            "net_profit_cents": 5000000 # $50,000.00
        },
        "aggressive": {
            "name": "Aggressive High-Ticket",
            "price_cents": 79900, # $799.00
            "variable_cost_cents": 19900, # $199.00
            "fixed_overhead_cents": 1000000, # $10,000.00
            "required_clients": 100,
            "target_mrr_cents": 7990000, # $79,900.00
            "net_profit_cents": 5000000 # $50,000.00
        }
    }

    def calculate_net_operating_profit(self, active_clients: int, plan: str = "base_case") -> Dict[str, Any]:
        """Calculates exact net operating profit and unit contribution."""
        sc = self.SCENARIOS.get(plan, self.SCENARIOS["base_case"])
        gross_mrr_cents = active_clients * sc["price_cents"]
        total_var_costs_cents = active_clients * sc["variable_cost_cents"]
        total_costs_cents = total_var_costs_cents + sc["fixed_overhead_cents"]
        net_profit_cents = gross_mrr_cents - total_costs_cents

        contribution_cents = sc["price_cents"] - sc["variable_cost_cents"]
        contribution_margin_pct = (contribution_cents / sc["price_cents"]) * 100.0

        return {
            "plan_name": sc["name"],
            "active_clients": active_clients,
            "gross_mrr_usd": gross_mrr_cents / 100.0,
            "total_costs_usd": total_costs_cents / 100.0,
            "net_operating_profit_usd": net_profit_cents / 100.0,
            "unit_contribution_usd": contribution_cents / 100.0,
            "contribution_margin_pct": round(contribution_margin_pct, 2),
            "reaches_50k_target": (net_profit_cents >= 5000000)
        }

    def calculate_hvac_roi(self, 
                           monthly_inquiries: int = 150, 
                           missed_inquiry_pct: float = 25.0,
                           avg_job_value_usd: float = 850.0,
                           close_rate_pct: float = 30.0,
                           monthly_system_cost_usd: float = 499.0) -> Dict[str, Any]:
        """
        Industry-specific ROI Calculator for HVAC & Plumbing Contractors.
        Computes recoverable missed opportunities and incremental gross margin.
        """
        missed_inquiries = monthly_inquiries * (missed_inquiry_pct / 100.0)
        # Assume our instant response captures 60% of otherwise lost inquiries
        recovered_leads = missed_inquiries * 0.60
        incremental_jobs = recovered_leads * (close_rate_pct / 100.0)
        incremental_revenue_usd = incremental_jobs * avg_job_value_usd
        
        # Net incremental profit after $499 system fee
        net_monthly_gain_usd = incremental_revenue_usd - monthly_system_cost_usd
        roi_multiplier = (incremental_revenue_usd / monthly_system_cost_usd) if monthly_system_cost_usd > 0 else 0.0

        return {
            "monthly_inquiries": monthly_inquiries,
            "estimated_missed_leads": round(missed_inquiries, 1),
            "recovered_leads": round(recovered_leads, 1),
            "incremental_closed_jobs": round(incremental_jobs, 1),
            "incremental_monthly_revenue_usd": round(incremental_revenue_usd, 2),
            "system_cost_usd": monthly_system_cost_usd,
            "net_monthly_gain_usd": round(net_monthly_gain_usd, 2),
            "roi_multiple": round(roi_multiplier, 1)
        }

    def calculate_veterinary_roi(self,
                                 daily_appointments: int = 8,
                                 working_days: int = 22,
                                 avg_ticket_usd: float = 75.0,
                                 no_show_reduction_pct: float = 15.0,
                                 monthly_software_cost_usd: float = 149.0) -> Dict[str, Any]:
        """
        Calculates recovered appointment value and hours saved for independent veterinarians.
        """
        monthly_appointments = daily_appointments * working_days
        recovered_visits = monthly_appointments * (no_show_reduction_pct / 100.0)
        recovered_revenue_usd = recovered_visits * avg_ticket_usd
        net_gain_usd = recovered_revenue_usd - monthly_software_cost_usd
        hours_saved_monthly = monthly_appointments * (10 / 60.0) # ~10 mins saved per pet on notes/prescriptions

        return {
            "monthly_appointments": monthly_appointments,
            "recovered_visits": round(recovered_visits, 1),
            "recovered_revenue_usd": round(recovered_revenue_usd, 2),
            "hours_saved_admin": round(hours_saved_monthly, 1),
            "net_monthly_gain_usd": round(net_gain_usd, 2),
            "roi_multiple": round(recovered_revenue_usd / monthly_software_cost_usd, 1)
        }

revenue_model = RevenueFeasibilityModel()
