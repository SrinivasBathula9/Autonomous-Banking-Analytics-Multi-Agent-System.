from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from ..agents.planner import planner
from ..agents.data_engineer import data_engineer
from ..agents.preprocessing import preprocessing
from ..agents.data_scientist import data_scientist
from ..agents.analyst import analyst
from ..agents.cdo import cdo

import json
from datetime import datetime

class AgentState(TypedDict):
    run_id: str
    query: str
    steps: List[str]
    data: dict
    insights: str
    debate: List[str]  # New: Structured dialogue
    explanations: dict  # New: Explainability drill-downs
    decision: str
    report_path: str

def plan_step(state: AgentState):
    print(f"[{state['run_id']}] Agent: Planner is coordinating...")
    db_service.log_audit("Planner", "Planning", f"Decomposing query: {state['query']}")
    state['steps'] = [planner.execute(state['query'])]
    state['report_path'] = ""
    return state

def data_fetch_step(state: AgentState):
    print(f"[{state['run_id']}] Agent: Data Engineer is ingesting...")
    db_service.log_audit("Data Engineer", "Data Ingestion", "Querying TransactionDB")
    state['data'] = {"log": data_engineer.execute("Querying TransactionDB"), "charts": []}
    return state

from ..services.database_service import DatabaseService
from ..services.modeling_service import ModelingService
from ..services.visualization_service import VisualizationService
from ..services.report_service import ReportService
from ..services.explainability_service import explainability_service

db_service = DatabaseService()
modeling_service = ModelingService()
viz_service = VisualizationService()
report_service = ReportService()

def preprocessing_step(state: AgentState):
    print(f"[{state['run_id']}] Agent: Cleaner is preprocessing...")
    db_service.log_audit("Preprocessing", "Data Cleaning", "Cleaning batch")
    state['data']['cleaning_log'] = preprocessing.execute("Cleaning batch", data=state['data'].get('log'))
    return state

def modeling_step(state: AgentState):
    print(f"[{state['run_id']}] Agent: Data Scientist is modeling...")
    db_service.log_audit("Data Scientist", "ML Modeling", "Proposing risk clusters and fraud scores")
    state['insights'] = data_scientist.execute("Running KMeans and Fraud Logit", db_service=db_service, modeling_service=modeling_service)
    
    # Start the debate
    state['debate'] = [f"Data Scientist: Proposed risk/fraud scores based on statistical anomalies and amount heuristics."]
    return state

def analyze_step(state: AgentState):
    print(f"[{state['run_id']}] Agent: Analyst is deriving insights...")
    db_service.log_audit("Analyst", "Insight Derivation", "Analyzing risk and volume")
    
    # Analyst evaluates trade-offs
    analyst_input = analyst.execute("Analyzing risk and volume.", db_service=db_service)
    state['insights'] += " | " + analyst_input
    state['debate'].append(f"Analyst: Evaluated trade-offs. Noted high volume in Luxury category might be Seasonal, not just Fraud. Recommending cautious observation.")
    
    # Generate multi-dimensional visualizations
    print(f"[{state['run_id']}] Generating comprehensive visual suite...")
    charts = []
    
    # 1. Spending Chart
    df_trans = db_service.run_query("SELECT category, SUM(amount) as amount FROM transactions GROUP BY category")
    c1 = viz_service.create_transaction_chart(df_trans, "Volume by Category", f"spending_{state['run_id']}.png")
    charts.append(c1.replace("\\", "/"))
    
    # 2. Risk Distribution
    df_cust = db_service.run_query("SELECT risk_score FROM customers")
    explanations = {}
    for _, row in df_cust.head(3).iterrows(): # Explain top 3
        explanations[str(row['risk_score'])] = explainability_service.get_risk_explanation({'risk_score': row['risk_score']})
    state['explanations'] = explanations

    c2 = viz_service.create_risk_distribution(df_cust, f"risk_{state['run_id']}.png")
    charts.append(c2.replace("\\", "/"))
    
    # 3. Asset Allocation
    df_assets = db_service.run_query("SELECT segment, total_assets FROM customers")
    c3 = viz_service.create_asset_pie_chart(df_assets, f"assets_{state['run_id']}.png")
    charts.append(c3.replace("\\", "/"))
    
    state['data']['charts'] = charts
    return state

def review_step(state: AgentState):
    print(f"[{state['run_id']}] Agent: CDO is reviewing governance compliance...")
    db_service.log_audit("CDO", "Final Review", "Granting strategic approval with justification")
    
    cdo_final = cdo.execute("Granting final strategic approval.")
    state['decision'] = cdo_final
    state['debate'].append(f"CDO: Finalized strategy. Reconciled Data Scientist's models with Analyst's market context. Justification: Low-impact risk segments allowed for VIP retention.")
    
    # Generate final report
    print(f"[{state['run_id']}] Generating executive report...")
    report_path = report_service.generate_executive_summary(
        analysis_results=state['insights'],
        chart_paths=state['data'].get('charts', [])
    )
    state['report_path'] = report_path.replace("\\", "/")
    return state

def persist_results(state: AgentState):
    print(f"[{state['run_id']}] Persisting run to Decision Intel history...")
    db_service.save_run(
        run_id=state['run_id'],
        query=state['query'],
        insights=state['insights'],
        decision=state['decision'],
        report_path=state['report_path'],
        full_state=json.dumps(state)
    )
    return state

def create_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("planner", plan_step)
    workflow.add_node("data_engineer", data_fetch_step)
    workflow.add_node("preprocessing", preprocessing_step)
    workflow.add_node("modeling", modeling_step)
    workflow.add_node("analyst", analyze_step)
    workflow.add_node("cdo", review_step)
    workflow.add_node("persistence", persist_results)
    
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "data_engineer")
    workflow.add_edge("data_engineer", "preprocessing")
    workflow.add_edge("preprocessing", "modeling")
    workflow.add_edge("modeling", "analyst")
    workflow.add_edge("analyst", "cdo")
    workflow.add_edge("cdo", "persistence")
    workflow.add_edge("persistence", END)
    
    return workflow.compile()

banking_workflow = create_workflow()
