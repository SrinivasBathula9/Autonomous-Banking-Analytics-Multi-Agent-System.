import matplotlib.pyplot as plt
import pandas as pd
import os

class VisualizationService:
    def __init__(self, output_dir: str = "charts"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def create_transaction_chart(self, df: pd.DataFrame, title: str, filename: str):
        """Generates a bar chart of transactions by category."""
        plt.figure(figsize=(10, 6))
        plt.style.use('dark_background')
        df.groupby('category')['amount'].sum().plot(kind='bar', color='#646cff')
        plt.title(title, pad=20)
        plt.xlabel('Category')
        plt.ylabel('Total Amount')
        path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(path, transparent=True)
        plt.close()
        return path

    def create_risk_distribution(self, df: pd.DataFrame, filename: str):
        """Generates a histogram of customer risk scores."""
        plt.figure(figsize=(10, 6))
        plt.style.use('dark_background')
        df['risk_score'].hist(bins=15, color='#ff6464', alpha=0.8)
        plt.title('Security Audit: Risk Distribution', pad=20)
        plt.xlabel('Risk Score (0-1)')
        plt.ylabel('Frequency')
        path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(path, transparent=True)
        plt.close()
        return path

    def create_asset_pie_chart(self, df: pd.DataFrame, filename: str):
        """Generates a pie chart of total assets by segment."""
        plt.figure(figsize=(8, 8))
        plt.style.use('dark_background')
        data = df.groupby('segment')['total_assets'].sum()
        data.plot(kind='pie', autopct='%1.1f%%', colors=['#646cff', '#4caf50', '#ffc107', '#ff5722'])
        plt.title('Asset Allocation by Segment', pad=20)
        plt.ylabel('')
        path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(path, transparent=True)
        plt.close()
        return path
