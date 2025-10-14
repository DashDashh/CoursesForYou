import requests
import json

BASE_URL = "http://localhost:5000"

def test_steps(module_id=None):
    print("Testing steps API...")

    if not module_id:
        print("Finding existing module...")
        response = requests.get(f"{BASE_URL}/api/modules")
        if response.status_code == 200:
            modules = response.json().get('modules', [])
            if modules:
                module_id = modules[0].get('id')
                print(f"Using module ID: {module_id}")
            else:
                print("No modules found")
                return
        else:
            print("Failed to fetch modules")
            return
        
    print(f"\n1. Creating step for module {module_id}...")
    step_data = {
        "number": 2,
        "step_type": 1
    }
    response = requests.post(f"{BASE_URL}/api/modules/{module_id}/steps", json=step_data)
    print(f"Create step status: {response.status_code}")

    if response.status_code == 201:
        data = response.json()
        step_id = data.get('step_id')
        print(f"Step created: (ID: {step_id})")
    else:
        print(f"Create step failed: {response.text}")
        return
    
    print("\n2. Getting module steps...")
    response = requests.get(f"{BASE_URL}/api/modules/{module_id}/steps")
    print(f"Get steps status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        steps = data.get('steps', [])
        print(f"Found {len(steps)} steps for module '{data.get('module_name')}'")

    print("\n3. Getting step by ID...")
    response = requests.get(f"{BASE_URL}/api/steps/{step_id}")
    print(f"Get step status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Step: (Number: {data.get('number')})")

if __name__ == "__main__":
    test_steps()