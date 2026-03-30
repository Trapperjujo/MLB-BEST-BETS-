import requests
import json
import os
import time

def check_status(app_id):
    if not os.path.exists(".appdeploy"):
        print("Error: No .appdeploy file found.")
        return
        
    with open(".appdeploy", "r") as f:
        config = json.load(f)
        
    url = config["endpoint"]
    api_key = config["api_key"]
    
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_app_status",
            "arguments": {
                "app_id": app_id
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {api_key}"
    }
    
    print(f"Polling status for app {app_id}...")
    while True:
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            result = data.get("result", {})
            content_str = result.get("content", [])[0].get("text", "{}")
            content = json.loads(content_str)
            
            status = content.get("deployment", {}).get("status")
            print(f"Status: {status}")
            
            if status in ["ready", "failed"]:
                print(f"\nFinal Result: {json.dumps(content, indent=2)}")
                break
                
            time.sleep(10)
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    import sys
    # Use 5827ba6f8bba4a3092 as the new default (Kinetic Edition)
    target_app = sys.argv[1] if len(sys.argv) > 1 else "5827ba6f8bba4a3092"
    check_status(target_app)
