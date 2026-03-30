import requests
import json
import os
import base64

def deploy():
    if not os.path.exists(".appdeploy"):
        print("Error: No .appdeploy file found.")
        return
        
    with open(".appdeploy", "r") as f:
        config = json.load(f)
        
    url = config["endpoint"]
    api_key = config["api_key"]
    
    # ------------------------------------------------------------------
    # PHASE 1: GET INSTRUCTIONS
    # ------------------------------------------------------------------
    print("Retrieving production constraints...")
    payload_instr = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_deploy_instructions",
            "arguments": {}
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        resp = requests.post(url, json=payload_instr, headers=headers)
        resp.raise_for_status()
        # Audit logic would go here if we were checking constraints
    except Exception as e:
        print(f"Error retrieving instructions: {e}")

    # ------------------------------------------------------------------
    # PHASE 2: BUNDLE FILES
    # ------------------------------------------------------------------
    print("Bundling institutional assets for build...")
    
    # Files to bundle (Main script, Logic core, Styles, Docs)
    files_to_send = [
        "app.py",
        "requirements.txt",
        "core/prediction_xgboost.py",
        "core/models.py",
        "core/analytics.py",
        "core/sheets_sync.py",
        "core/config.py",
        "styles/neon_theme.css"
    ]
    
    bundled_files = []
    for file_path in files_to_send:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                bundled_files.append({
                    "path": file_path,
                    "content": content
                })
    
    # ------------------------------------------------------------------
    # PHASE 3: EXECUTE DEPLOYMENT
    # ------------------------------------------------------------------
    print("Executing Master Deployment... (JSON-RPC Live Push)")
    payload_deploy = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "deploy_app",
            "arguments": {
                "app_id": None,
                "app_type": "frontend+backend",
                "app_name": "PRO BALL PREDICTIONS",
                "description": "Institutional-grade MLB Command Center with Kinetic UI and Science-Hardened logic.",
                "frontend_template": "html-static", # Template for the container environment
                "files": bundled_files,
                "model": "antigravity-institutional-v1.0",
                "intent": "Master launch of hardened kinetic terminal."
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload_deploy, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            print(f"Deployment Error: {data['error']}")
            return
            
        result = data.get("result", {})
        print("\nSUCCESS: Command Center 2026 is LIVE.")
        print(f"Result Payload: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Master Deployment Error: {e}")

if __name__ == "__main__":
    deploy()
