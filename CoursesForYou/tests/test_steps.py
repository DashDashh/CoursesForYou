import requests

BASE_URL = "http://localhost:5000"

def test_steps(module_id=None):
    print("Testing steps API...")

    if not module_id:
        print("Finding existing module...")
        response = requests.get(f"{BASE_URL}/api/courses")
        if response.status_code == 200:
            courses = response.json().get('courses', [])
            if courses:
                course_id = courses[0].get('id')
                response = requests.get(f"{BASE_URL}/api/courses/{course_id}/modules")
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
            else:
                print("No courses found")
                return
        else:
            print("Failed to fetch courses")
            return
        
    print(f"\n1. Creating theory step for module {module_id}...")
    step_data_theory = {
        "number": 3,
        "step_type": 1,
        "text": "Это теоретическая часть о основах Python"
    }
    
    response = requests.post(f"{BASE_URL}/api/modules/{module_id}/steps", json=step_data_theory)
    print(f"Create theory step status: {response.status_code}")

    if response.status_code == 201:
        data = response.json()
        theory_step_id = data.get('step_id')
        print(f"Theory step created: (ID: {theory_step_id})")
    else:
        print(f"Create theory step failed: {response.text}")
        return
    
    print(f"\n2. Creating task step for module {module_id}...")
    step_data_task = {
        "number": 4,
        "step_type": 2,
        "question": "Что такое переменная в Python?",
        "answer": "Именованная область памяти для хранения данных"
    }
    
    response = requests.post(f"{BASE_URL}/api/modules/{module_id}/steps", json=step_data_task)
    print(f"Create task step status: {response.status_code}")

    if response.status_code == 201:
        data = response.json()
        task_step_id = data.get('step_id')
        print(f"Task step created: (ID: {task_step_id})")
    else:
        print(f"Create task step failed: {response.text}")
    
    print("\n3. Getting module steps...")
    response = requests.get(f"{BASE_URL}/api/modules/{module_id}/steps")
    print(f"Get steps status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        steps = data.get('steps', [])
        print(f"Found {len(steps)} steps for module '{data.get('module_name')}'")
    
    print("\n4. Getting step by ID...")
    response = requests.get(f"{BASE_URL}/api/steps/{theory_step_id}")
    print(f"Get step status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Step: Number={data.get('number')}, Type={data.get('step_type')}")
    
    return theory_step_id, task_step_id

if __name__ == "__main__":
    test_steps()