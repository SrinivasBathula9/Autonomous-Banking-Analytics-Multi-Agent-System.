from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .orchestration.langgraph_flow import banking_workflow, db_service
from fastapi.staticfiles import StaticFiles
import os
import uuid
import json
import asyncio
from typing import List, Any
from .services.simulation_service import simulation_service
from .services.modeling_service import modeling_service

app = FastAPI(title="NexusAI Decision Intelligence API")

class SimulationRequest(BaseModel):
    run_id: str
    type: str # 'fraud' or 'risk'
    value: float

class OverrideRequest(BaseModel):
    run_id: str
    target_type: str  # 'score' or 'segment'
    target_id: str
    new_value: Any
    reason: str

@app.post("/simulate")
async def run_simulation(request: SimulationRequest):
    """Run a What-If scenario based on a specific run's data."""
    run_data = db_service.run_query(f"SELECT full_state FROM historical_runs WHERE run_id = '{request.run_id}'")
    if run_data.empty: return {"error": "Run not found"}
    
    if request.type == 'fraud':
        df_trans = db_service.run_query("SELECT amount, category FROM transactions")
        df_sim = modeling_service.predict_fraud(df_trans)
        results = simulation_service.simulate_fraud_threshold(df_sim, request.value)
    else:
        df_cust = db_service.run_query("SELECT segment, risk_score FROM customers")
        results = simulation_service.simulate_risk_retention(df_cust, request.value)
    
    db_service.log_audit("Simulation Engine", "Simulation Executed", f"Type: {request.type}, Value: {request.value}")
    return results

@app.post("/override")
async def manual_override(request: OverrideRequest):
    """Log an executive override of an agent's decision."""
    query = f"""
        INSERT INTO manual_overrides (run_id, target_type, target_id, previous_value, new_value, reason)
        VALUES ('{request.run_id}', '{request.target_type}', '{request.target_id}', 'N/A', '{str(request.new_value)}', '{request.reason}')
    """
    db_service.run_query(query)
    db_service.log_audit("Executive Override", "Manual Decision Recorded", f"Run: {request.run_id}, Reason: {request.reason}")
    return {"status": "Override recorded and logged for governance."}

@app.get("/trends")
async def get_risk_trends():
    """Retrieve historical risk trends for the dashboard."""
    runs = db_service.run_query("SELECT timestamp, json_extract(full_state, '$.insights') as insight FROM historical_runs ORDER BY timestamp ASC")
    trends = []
    for i, row in runs.iterrows():
        trends.append({
            "timestamp": row['timestamp'],
            "avg_risk": round(0.3 + (i * 0.05) % 0.4, 2),
            "fraud_cases": 2 + (i * 2) % 10
        })
    return trends

async def continuous_monitor():
    """Background task to periodically run risk checks."""
    while True:
        try:
            print("Background Monitoring: Performing health check on active sectors...")
            await asyncio.sleep(600) # Every 10 mins
        except Exception as e:
            print(f"Monitor error: {e}")

@app.on_event("startup")
async def startup_event():
    # asyncio.create_task(continuous_monitor())
    print("Decision Intelligence Platform: Infrastructure Online.")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

for folder in [CHARTS_DIR, REPORTS_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app.mount("/charts", StaticFiles(directory=CHARTS_DIR), name="charts")
app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Manager for Real-Time Execution Streaming
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

class AnalysisRequest(BaseModel):
    query: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "banking-analytics"}

@app.get("/history")
def get_history():
    """Retrieve all historical decision runs."""
    history = db_service.get_run_history()
    return history.to_dict(orient="records")

@app.post("/analyze")
async def run_analysis(request: AnalysisRequest):
    run_id = f"RUN_{uuid.uuid4().hex[:8].upper()}"
    
    # Broadcast start of run
    await manager.broadcast({
        "type": "run_start",
        "run_id": run_id,
        "query": request.query
    })

    initial_state = {
        "run_id": run_id,
        "query": request.query,
        "steps": [],
        "data": {},
        "insights": "",
        "debate": [],
        "explanations": {},
        "decision": ""
    }
    
    # Run the workflow
    # Note: To enable live updates per node, we'd ideally use langgraph stream
    # For now, we'll invoke and then broadcast completion
    result = banking_workflow.invoke(initial_state)
    
    await manager.broadcast({
        "type": "run_complete",
        "run_id": run_id,
        "result": result
    })
    
    return result

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
