import requests

BASE_URL = "http://localhost:5000"

def test_theories_tasks(theory_step_id, task_step_id):
    print("Testing theories and tasks API...")
    
    print("\n1. Testing theory endpoints...")
    
    response = requests.get(f"{BASE_URL}/api/steps/{theory_step_id}/theory")
    print(f"Get theory by step status: {response.status_code}")
    
    if response.status_code == 200:
        theory_data = response.json()
        theory_id = theory_data.get('id')
        print(f"Theory found: ID={theory_id}")
        
        update_data = {"text": "Обновленный текст теории о Python"}
        response = requests.put(f"{BASE_URL}/api/theories/{theory_id}", json=update_data)
        print(f"Update theory status: {response.status_code}")
        
        if response.status_code == 200:
            print("Theory updated successfully")
     
    print("\n2. Testing task endpoints...")
    
    response = requests.get(f"{BASE_URL}/api/steps/{task_step_id}/task")
    print(f"Get task by step status: {response.status_code}")
    
    if response.status_code == 200:
        task_data = response.json()
        task_id = task_data.get('id')
        print(f"Task found: ID={task_id}")
        
        update_data = {
            "question": "Что такое функция в Python?",
            "answer": "Блок кода, который выполняет определенную задачу"
        }
        response = requests.put(f"{BASE_URL}/api/tasks/{task_id}", json=update_data)
        print(f"Update task status: {response.status_code}")
        
        check_data = {"answer": "Блок кода, который выполняет определенную задачу"}
        response = requests.post(f"{BASE_URL}/api/tasks/{task_id}/check-answer", json=check_data)
        print(f"Check answer status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Answer check: {result.get('is_correct')}")

if __name__ == "__main__":
    test_theories_tasks(1, 2)