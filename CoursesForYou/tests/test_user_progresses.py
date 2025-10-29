import requests

BASE_URL = "http://localhost:5000"

def test_user_progresses(user_id, step_id, course_id, module_id):
    print("Testing user_progress API...")

    print("\n1. Testing create/update step progress...")
    progress_data = {"status": "NOT_BEGIN"}
    response = requests.post(f"{BASE_URL}/api/user_progress/user/{user_id}/step/{step_id}", json=progress_data)
    print(f"First attempt status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Progress created: ID={data['progress_id']}, tries={data['num_tries']}, status={data['status']}")

    progress_data = {"status": "DONE"}
    response = requests.put(f"{BASE_URL}/api/user_progress/user/{user_id}/step/{step_id}", json=progress_data)
    print(f"Second attempt status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Progress updated: tries={data['num_tries']}, status={data['status']}")

    print("\n2. Testing get course progress...")
    response = requests.get(f"{BASE_URL}/api/user_progress/user/{user_id}/course/{course_id}")
    print(f"Get course progress status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Course progress: {data['completed_steps']}/{data['total_steps']} steps completed")
        print(f"   Progress: {data['progress_percentage']}%")
        print(f"   Not started: {data['not_started_steps']}, In progress: {data['in_progress_steps']}")

    print("\n3. Testing get module progress...")
    response = requests.get(f"{BASE_URL}/api/user_progress/user/{user_id}/module/{module_id}")
    print(f"Get module progress status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Module progress: {data['completed_steps']}/{data['total_steps']} steps completed")
        print(f"   Module: {data['module_name']}")
        print(f"   Steps details: {len(data['steps'])} steps found")
        
        for i, step in enumerate(data['steps'][:3]):
            print(f"     Step {i+1}: {step['step_type']}, status={step['status']}, tries={step['num_tries']}")
    else:
        print(f"Error {response.status_code}. Check server logs for details.")