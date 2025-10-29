import requests

BASE_URL = "http://localhost:5000"

def test_user_courses(user_id, course_id):
    print("Testing user_courses API...")
    
    print("\n1. Testing enrollment...")
    response = requests.post(f"{BASE_URL}/api/user/{user_id}/course/{course_id}")
    print(f"Enroll user to course status: {response.status_code}")

    if response.status_code == 201:
        print("User enrolled successfully")
    elif response.status_code == 409:
        print("User already enrolled")

    print("\n2. Testing get user courses...")
    response = requests.get(f"{BASE_URL}/api/user/{user_id}/courses")
    print(f"Get user courses status: {response.status_code}")

    if response.status_code == 200:
        courses = response.json()
        print(f"User has {len(courses)} courses:")
        for course in courses:
            print(f"  - {course['course_name']} (ID: {course['course_id']})")

    print("\n3. Testing get course users...")
    response = requests.get(f"{BASE_URL}/api/course/{course_id}/users")
    print(f"Get course users status: {response.status_code}")

    if response.status_code == 200:
        users = response.json()
        print(f"Course has {len(users)} users:")
        for user in users:
            print(f"  - {user['login']} (ID: {user['user_id']})")

    print("\n4. Testing unenrollment...")
    response = requests.delete(f"{BASE_URL}/api/user/{user_id}/course/{course_id}")
    print(f"Unenroll user from course status: {response.status_code}")

    if response.status_code == 200:
        print("User unenrolled successfully")

    print("\n5. Testing after unenrollment...")
    response = requests.get(f"{BASE_URL}/api/user/{user_id}/courses")
    if response.status_code == 200:
        courses = response.json()
        print(f"User now has {len(courses)} courses")