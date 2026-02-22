import requests
import json
import time

def test_intelligence_suite():
    base_url = "http://localhost:8000"
    
    print("--- 1. Testing Intelligence Run (/analyze) ---")
    analyze_payload = {"query": "Assess high-risk anomalies in the retail sector."}
    try:
        response = requests.post(f"{base_url}/analyze", json=analyze_payload)
        result = response.json()
        
        if "run_id" in result:
            print(f"✅ Analysis Started. Run ID: {result['run_id']}")
            print(f"✅ Debate Sequence: {len(result.get('debate', []))} messages found.")
            print(f"✅ Explainability Trace: {len(result.get('explanations', {}))} entries found.")
            
            run_id = result['run_id']
            
            print("\n--- 2. Testing Simulation Engine (/simulate) ---")
            sim_payload = {"run_id": run_id, "type": "fraud", "value": 0.8}
            sim_res = requests.post(f"{base_url}/simulate", json=sim_payload)
            sim_data = sim_res.json()
            if "parameter" in sim_data:
                print(f"✅ Simulation Successful: {sim_data['parameter']} updated from {sim_data['value_before']} to {sim_data['value_after']}")
                print(f"✅ Business Impact: {sim_data['business_impact']}")
            else:
                print(f"❌ Simulation Failed: {sim_data}")

            print("\n--- 3. Testing History Persistence (/history) ---")
            hist_res = requests.get(f"{base_url}/history")
            history = hist_res.json()
            if any(r['run_id'] == run_id for r in history):
                print(f"✅ Run Persistence verified in history.")
            else:
                print(f"❌ Run ID not found in history.")
        else:
            print(f"❌ Analysis failed to provide Run ID: {result}")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")

if __name__ == "__main__":
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(5)
    test_intelligence_suite()
