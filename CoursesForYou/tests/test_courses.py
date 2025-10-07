import requests
import json

BASE_URL = "http://localhost:5000"
COURSES_URL = f"{BASE_URL}/api/courses"

def test_courses(token_info):
    print("Testing courses...")
    
    headers = {}
    if token_info and isinstance(token_info, dict):
        print(f"Testing with user: {token_info.get('login')} (ID: {token_info.get('user_id')})")
    
    try:
        print("\n1. Testing GET courses...")
        response = requests.get(COURSES_URL, headers=headers)
        print(f"Get courses status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Get courses successful!")
            courses = data.get('courses', [])
            print(f"Found {len(courses)} courses")
        else:
            print(f"Get courses failed: {response.text}")
        
        print("\n2. Testing POST course...")
        
        teacher_id = token_info.get('user_id') if token_info else 1
        
        course_data = {
            "name": "Python Programming",
            "id_teacher": teacher_id,
            "description": "Learn Python from scratch",
            "theme_id": 4,
            "level": 1
        }
        
        print(f"Sending course data: {course_data}")
        
        response = requests.post(COURSES_URL, json=course_data)
        print(f"Create course status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("Create course successful!")
            print(f"Course created: {data.get('course', {}).get('name')} (ID: {data.get('course_id')})")
        else:
            print(f"Create course failed: {response.text}")
        
        print("\n3. Verifying course was added...")
        response = requests.get(COURSES_URL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            courses = data.get('courses', [])
            print(f"Now found {len(courses)} courses")
            
    except Exception as e:
        print(f"Courses test error: {e}")

if __name__ == "__main__":
    test_courses(None)