# Autonomous Banking Analytics Platform
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, multi-agent platform for autonomous financial data analysis, predictive modeling, and executive reporting. Powered by **FastAPI**, **LangGraph**, and **React**.

## 🚀 Overview
This system utilizes a team of specialized AI agents to orchestrate a complete data-to-decision pipeline. It ingests banking transactions, cleanses metadata, runs machine learning models for risk and segmentation, and generates board-ready reports—all autonomously.

## 🏗️ Architecture
The platform is split into a robust Python backend and a modern React frontend.

### 📁 Project Structure
```text
Bnaking-Multi-Agent-System/
├── app/                  # Backend FastAPI Application
│   ├── agents/           # Specialized AI Agent Brains (Planner, Analyst, etc.)
│   ├── orchestration/    # LangGraph State Machine & Workflow Logic
│   ├── services/         # Core Business Logic (DB, ML, Visualization)
│   └── main.py           # API Server Entry Point
├── frontend/             # React Dashboard (Vite + TypeScript)
├── charts/               # Generated Visual Insights (PNG)
├── reports/              # Executive Briefings (Markdown)
└── banking_data.db       # SQLite Database
```

## 🤖 AI Agent Team
The workflow is orchestrated by a 6-node state machine:

| Agent | Responsibility |
| :--- | :--- |
| **Planner** | Decomposes business queries into executable technical steps. |
| **Data Engineer** | Synchronizes data from the core banking ledger (SQLite). |
| **Preprocessing** | Normalizes features and handles missing data for ML purity. |
| **Data Scientist** | Executes KMeans Clustering and Predictive Fraud probability models. |
| **Analyst** | Derives high-level SQL insights (e.g., spending trends, high-risk flags). |
| **CDO (Governance)** | Performs final strategic review and approves the Executive Briefing. |

## 📊 Data & Models
- **Database**: SQLite with automated seeding for `transactions` and `customers`.
- **Modeling**: 
    - **Customer Segmentation**: Scikit-learn KMeans clustering.
    - **Risk Scoring**: Predictive logit-based fraud probability.
- **Visuals**: Matplotlib-generated studio-dark charts (Spending, Risk, Assets).

## 🛠️ Runbook

### 1. Prerequisites
- Python 3.10+
- Node.js 18+

### 2. Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
python -m app.main
```
*Server runs at `http://localhost:8000`*

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Dashboard runs at `http://localhost:5173`*

## 🎯 Use Cases
- **Portfolio Health Audit**: Instant assessment of credit and transaction risk.
- **VIP Customer Identification**: Automated segmentation for targeted marketing.
- **Executive Decision Support**: Generating board-ready briefings in seconds instead of hours.
- **Anomalous Volume Detection**: Identifying unusual spending categories across the ledger.

---
*Built with Antigravity AI - Advanced Agentic Coding Framework.*
