import requests
import time
import json
import random

CAMUNDA_URL = "http://localhost:8080/engine-rest"
WORKER_ID = "python-worker"

def fetch_and_lock(topic_name):
    url = f"{CAMUNDA_URL}/external-task/fetchAndLock"
    payload = {
        "workerId": WORKER_ID,
        "maxTasks": 1,
        "usePriority": True,
        "topics": [{"topicName": topic_name, "lockDuration": 10000}]
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching tasks: {e}")
    return []

def complete_task(task_id, variables={}):
    url = f"{CAMUNDA_URL}/external-task/{task_id}/complete"
    payload = {
        "workerId": WORKER_ID,
        "variables": variables
    }
    try:
        requests.post(url, json=payload)
        print(f"Completed task {task_id}")
    except Exception as e:
         print(f"Error completing task {task_id}: {e}")

def handle_tasks():
    print(f"Worker {WORKER_ID} started. Connects to {CAMUNDA_URL}")
    while True:
        try:
            # Handle LLM Request (Nahrungszyklusprozess)
            tasks = fetch_and_lock("requestLLM")
            for task in tasks:
                print(f"Processing requestLLM task {task['id']}")
                # Simulate LLM processing
                variables = {
                    "llmResponse": {"value": "Generated Nutrition Plan: 200g dry food daily.", "type": "String"}
                }
                # Call Camunda to complete
                complete_task(task['id'], variables)

            # Handle Purchase Recommendation (Nahrungszyklusprozess)
            tasks = fetch_and_lock("requestPurchaseRecommendation")
            for task in tasks:
                print(f"Processing requestPurchaseRecommendation task {task['id']}")
                variables = {
                    "recommendation": {"value": "SuperPremium Food Brand", "type": "String"}
                }
                complete_task(task['id'], variables)

            # Handle Database Update (Main Process)
            tasks = fetch_and_lock("updateDatabase")
            for task in tasks:
                print(f"Processing updateDatabase task {task['id']}")
                # Simulate DB update
                complete_task(task['id'])

        except Exception as e:
            print(f"Worker loop error: {e}")

        time.sleep(1)

if __name__ == "__main__":
    handle_tasks()
