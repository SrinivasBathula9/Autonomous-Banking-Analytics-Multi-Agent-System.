from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np

class ModelingService:
    def __init__(self):
        self.models = {}

    def train_customer_segmentation(self, df: pd.DataFrame, n_clusters: int = 4):
        """Simple KMeans clustering for customer segmentation with robustness check."""
        if len(df) < n_clusters:
            n_clusters = max(1, len(df))
            
        features = df[['risk_score', 'total_assets']]
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df['segment_id'] = kmeans.fit_predict(features)
        self.models['segmentation'] = kmeans
        return df

    def predict_fraud(self, transaction_df: pd.DataFrame):
        """Calculates fraud probability based on amount and category features."""
        # Logic: High amount + Luxury/Electronics = Higher probability
        def calc_prob(row):
            base = 0.1
            if row['amount'] > 10000: base += 0.4
            if row['category'] in ['Luxury', 'Electronics']: base += 0.2
            return min(0.95, base + (np.random.rand() * 0.05))

        transaction_df['fraud_probability'] = transaction_df.apply(calc_prob, axis=1)
        return transaction_df

modeling_service = ModelingService()
