import requests
import json
import os

def register():
    url = "https://api-v2.appdeploy.ai/mcp/api-key"
    payload = {"client_name": "antigravity"}
    headers = {"Content-Type": "application/json"}
    
    print(f"Registering institutional agent with {url}...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        api_key = data.get("api_key")
        if not api_key:
            print(f"Failed to retrieve API key: {data}")
            return
            
        config = {
            "api_key": api_key,
            "endpoint": "https://api-v2.appdeploy.ai/mcp"
        }
        
        with open(".appdeploy", "w") as f:
            json.dump(config, f, indent=2)
            
        print("Success: AppDeploy credentials secured and saved to .appdeploy")
        
        # Add to .gitignore
        if os.path.exists(".gitignore"):
            with open(".gitignore", "a") as f:
                f.write("\n.appdeploy\n")
            print("Security: .appdeploy added to .gitignore.")
            
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    register()
