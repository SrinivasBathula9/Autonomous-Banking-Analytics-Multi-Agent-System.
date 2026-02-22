import pandas as pd
import numpy as np
from typing import Dict, List, Any

class ExplainabilityService:
    """Provides justifications and SHAP-style feature importance for AI decisions."""

    def get_risk_explanation(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Explains why a customer has a certain risk score."""
        # Simulated SHAP values based on assets and activity
        assets = customer_data.get('total_assets', 0)
        risk_base = customer_data.get('risk_score', 0.5)
        
        features = {
            "Total Assets": -0.2 if assets > 100000 else 0.1,
            "Transaction Frequency": 0.15 if risk_base > 0.6 else -0.05,
            "Cross-Border Activity": 0.3 if risk_base > 0.7 else 0.0,
            "Historical Compliance": -0.1 if risk_base < 0.3 else 0.05
        }
        
        # Normalize to ensure they sum to something meaningful
        total = sum(abs(v) for v in features.values())
        if total > 0:
            importance = {k: (v / total) * 100 for k, v in features.items()}
        else:
            importance = {k: 0 for k in features.keys()}

        return {
            "confidence_score": 0.85 + (np.random.rand() * 0.1),
            "feature_importance": importance,
            "plain_english": self._generate_justification(importance, risk_base)
        }

    def _generate_justification(self, importance: Dict[str, float], score: float) -> str:
        top_feature = max(importance, key=lambda k: abs(importance[k]))
        direction = "increasing" if importance[top_feature] > 0 else "decreasing"
        
        if score > 0.7:
            return f"High risk flag primarily driven by {top_feature}, {direction} the probability of anomaly detection."
        elif score < 0.3:
            return f"Low risk profile maintained due to strong {top_feature} metrics."
        else:
            return f"Balanced risk profile with {top_feature} as the primary influence factor."

explainability_service = ExplainabilityService()
