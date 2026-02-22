import pandas as pd
import numpy as np
from typing import Dict, Any

class SimulationService:
    """Executes 'What-If' scenarios for banking decisions."""

    def simulate_fraud_threshold(self, df: pd.DataFrame, threshold: float) -> Dict[str, Any]:
        """Simulates impact of changing the fraud detection sensitivity."""
        # Current (using default 0.5)
        current_flagged = len(df[df['fraud_probability'] > 0.5])
        
        # Simulated
        simulated_flagged = len(df[df['fraud_probability'] > threshold])
        
        impact = {
            "parameter": "Fraud Threshold",
            "value_before": 0.5,
            "value_after": threshold,
            "count_before": current_flagged,
            "count_after": simulated_flagged,
            "delta": simulated_flagged - current_flagged,
            "business_impact": "Lowering threshold increases security but raises false positives." if threshold < 0.5 else "Raising threshold reduces false positives but increases risk of undetected fraud."
        }
        return impact

    def simulate_risk_retention(self, df: pd.DataFrame, risk_cap: float) -> Dict[str, Any]:
        """Simulates impact of adjusting the risk score cutoff for VIP retention."""
        # VIPs often get higher leeway. Adjusting the leeway cap.
        vips = df[df['segment'] == 'VIP']
        flagged_before = len(vips[vips['risk_score'] > 0.7])
        
        flagged_after = len(vips[vips['risk_score'] > risk_cap])
        
        return {
            "parameter": "VIP Risk Allowance",
            "value_before": 0.7,
            "value_after": risk_cap,
            "vips_affected": abs(flagged_after - flagged_before),
            "business_impact": "Increasing allowance improves VIP retention but relaxes governance." if risk_cap > 0.7 else "Reducing allowance tightens security but may churn high-value clients."
        }

simulation_service = SimulationService()
