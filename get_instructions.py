import requests
import json
import os

def get_instructions():
    if not os.path.exists(".appdeploy"):
        print("Error: No .appdeploy file found.")
        return
        
    with open(".appdeploy", "r") as f:
        config = json.load(f)
        
    url = config["endpoint"]
    api_key = config["api_key"]
    
    payload = {
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
        "Authorization": f"Bearer {api_key}"
    }
    
    print(f"📡 Retrieving deployment instructions from {url}...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            print(f"❌ RPC Error: {data['error']}")
            return
            
        result = data.get("result", {})
        content = result.get("content", [])
        for item in content:
            if item.get("type") == "text":
                print(f"\n--- INSTRUCTIONS ---\n{item['text']}\n")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_instructions()
