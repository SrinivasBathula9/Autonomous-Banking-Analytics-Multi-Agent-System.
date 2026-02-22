import sqlite3
import pandas as pd
from typing import List, Dict, Any

class DatabaseService:
    def __init__(self, db_path: str = "banking_data.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Seed initial banking data for demonstration."""
        conn = sqlite3.connect(self.db_path)
        # Create dummy transactions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                customer_id TEXT,
                amount REAL,
                category TEXT,
                timestamp DATETIME,
                location TEXT,
                merchant TEXT
            )
        """)
        # Create dummy customers table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                name TEXT,
                risk_score REAL,
                segment TEXT,
                total_assets REAL
            )
        """)
        # Create historical runs table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS historical_runs (
                run_id TEXT PRIMARY KEY,
                timestamp DATETIME,
                query TEXT,
                insights TEXT,
                decision TEXT,
                report_path TEXT,
                full_state TEXT
            )
        """)
        # Create manual overrides table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS manual_overrides (
                override_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                original_decision TEXT,
                new_decision TEXT,
                reason TEXT,
                timestamp DATETIME,
                FOREIGN KEY(run_id) REFERENCES historical_runs(run_id)
            )
        """)
        # Create simulation results table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS simulation_results (
                sim_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                parameterTEXT TEXT,
                value_before REAL,
                value_after REAL,
                impact_score REAL,
                timestamp DATETIME,
                FOREIGN KEY(run_id) REFERENCES historical_runs(run_id)
            )
        """)
        # Create audit logs table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                agent TEXT,
                action TEXT,
                details TEXT
            )
        """)
        # Check if empty, then seed
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions")
        if cursor.fetchone()[0] == 0:
            transactions = [
                ('tx1', 'cust1', 1200.50, 'Groceries', '2026-02-21 10:00:00', 'New York', 'SuperMart'),
                ('tx2', 'cust2', 5000.00, 'Electronics', '2026-02-21 11:30:00', 'London', 'TechWorld'),
                ('tx3', 'cust1', 45.00, 'Dining', '2026-02-21 12:15:00', 'New York', 'CafeLuxe'),
                ('tx4', 'cust3', 15000.00, 'Luxury', '2026-02-21 14:00:00', 'Dubai', 'GoldRetail')
            ]
            cursor.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?)", transactions)
            
            customers = [
                ('cust1', 'Alice Johnson', 0.15, 'Retail', 50000.00),
                ('cust2', 'Bob Smith', 0.45, 'Corporate', 200000.00),
                ('cust3', 'Charlie Brown', 0.85, 'VIP', 1000000.00),
                ('cust4', 'David Wilson', 0.10, 'Retail', 15000.00),
                ('cust5', 'Eva Green', 0.30, 'Private', 750000.00),
                ('cust6', 'Frank White', 0.60, 'SME', 120000.00)
            ]
            cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers)
            conn.commit()
        conn.close()

    def run_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return a DataFrame."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_summary(self, table: str) -> Dict[str, Any]:
        """Get basic statistics for a table."""
        df = self.run_query(f"SELECT * FROM {table}")
        return df.describe().to_dict()

    def log_audit(self, agent: str, action: str, details: str = ""):
        """Log an agent action to the audit table."""
        from datetime import datetime
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO audit_logs (timestamp, agent, action, details) VALUES (?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), agent, action, details)
        )
        conn.commit()
        conn.close()

    def save_run(self, run_id: str, query: str, insights: str, decision: str, report_path: str, full_state: str):
        """Persist a full analysis run."""
        from datetime import datetime
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO historical_runs (run_id, timestamp, query, insights, decision, report_path, full_state) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), query, insights, decision, report_path, full_state)
        )
        conn.commit()
        conn.close()

    def get_run_history(self) -> pd.DataFrame:
        """Retrieve all previous runs."""
        return self.run_query("SELECT * FROM historical_runs ORDER BY timestamp DESC")
