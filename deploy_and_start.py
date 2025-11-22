import requests
import os

CAMUNDA_URL = "http://localhost:8080/engine-rest"

def deploy():
    url = f"{CAMUNDA_URL}/deployment/create"

    # Ensure files exist
    if not os.path.exists('DPE_Haustierprozess.bpmn') or not os.path.exists('Nahrungszyklusprozess.bpmn'):
        print("BPMN files not found!")
        return

    files = {
        'data1': open('DPE_Haustierprozess.bpmn', 'rb'),
        'data2': open('Nahrungszyklusprozess.bpmn', 'rb'),
    }

    data = {
        'deployment-name': 'HaustierProzessDeployment',
        'enable-duplicate-filtering': 'true',
        'deploy-changed-only': 'true'
    }

    try:
        print(f"Deploying to {url}...")
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        print(f"Deployment successful. Deployment ID: {response.json()['id']}")

        # Print deployed process definitions
        definitions = response.json().get('deployedProcessDefinitions', {})
        for key, val in definitions.items():
            print(f"Deployed Process: {key} -> {val['id']}")

    except Exception as e:
        print(f"Deployment failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(e.response.text)

def start_process():
    # Start the main process
    # The ID of the main process in DPE_Haustierprozess.bpmn is 'Process_17qlqmt'
    # You might want to rename it to something more meaningful in the XML if you like,
    # but for now we use the existing ID.
    key = "Process_17qlqmt"
    url = f"{CAMUNDA_URL}/process-definition/key/{key}/start"

    headers = {'Content-Type': 'application/json'}
    payload = {
        "variables": {
            "haustierId": {"value": "Pet-12345", "type": "String"},
            "vorraete": {"value": 5, "type": "Integer"}
        }
    }

    try:
        print(f"Starting process instance for key '{key}'...")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"Process instance started. ID: {response.json()['id']}")
    except Exception as e:
        print(f"Failed to start process: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(e.response.text)

if __name__ == "__main__":
    deploy()
    # Uncomment the next line to start a process immediately after deployment
    # start_process()
