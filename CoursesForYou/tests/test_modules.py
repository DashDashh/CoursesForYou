import requests
import json

BASE_URL = "http://localhost:5000"

def test_modules(course_id=None):
    print("Testing modules API...")
    
    if not course_id:
        print("Finding existing course...")
        response = requests.get(f"{BASE_URL}/api/courses")
        if response.status_code == 200:
            courses = response.json().get('courses', [])
            if courses:
                course_id = courses[0].get('id')
                print(f"Using course ID: {course_id}")
            else:
                print("No courses found")
                return
        else:
            print("Failed to fetch courses")
            return
    
    print(f"\n1. Creating module for course {course_id}...")
    module_data = {
        "name": "Введение в Python",
        "number": 1
    }
    
    response = requests.post(f"{BASE_URL}/api/courses/{course_id}/modules", json=module_data)
    print(f"Create module status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        module_id = data.get('module_id')
        print(f"Module created: {data.get('module', {}).get('name')} (ID: {module_id})")
    else:
        print(f"Create module failed: {response.text}")
        return
    
    print("\n2. Getting course modules...")
    response = requests.get(f"{BASE_URL}/api/courses/{course_id}/modules")
    print(f"Get modules status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        modules = data.get('modules', [])
        print(f"Found {len(modules)} modules for course '{data.get('course_name')}'")
    
    print("\n3. Getting module by ID...")
    response = requests.get(f"{BASE_URL}/api/modules/{module_id}")
    print(f"Get module status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Module: {data.get('name')} (Number: {data.get('number')})")

if __name__ == "__main__":
    test_modules()