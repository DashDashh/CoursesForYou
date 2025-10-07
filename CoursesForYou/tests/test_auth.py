import requests
import json

BASE_URL = "http://localhost:5000"
REGISTER_URL = f"{BASE_URL}/api/auth/register"
LOGIN_URL = f"{BASE_URL}/api/auth/login"

def test_auth():
    print("Testing authentication...")
    
    register_data = {
        "login": "newuser",
        "password": "GoodPassw_422!"
    }
    
    try:
        print("1. Testing registration...")
        response = requests.post(REGISTER_URL, json=register_data)
        print(f"Register status: {response.status_code}")
        
        if response.status_code == 201:
            print("Registration successful!")
            print(f"Register response: {response.json()}")
        else:
            print(f"Registration failed: {response.text}")
        
        print("\n2. Testing login with new user...")
        login_data = {
            "login": "newuser",
            "password": "GoodPassw_422!"
        }
        
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Login successful!")
            print(f"Login response: {data}")

            user_info = data.get('user', {})
            return {
                "user_id": user_info.get('id'),
                "login": user_info.get('login'),
                "token": f"test_token_{user_info.get('id')}" 
            }
        else:
            print(f"Login failed: {response.text}")
            
        print("\n3. Testing login with test user from DB...")
        login_test_data = {
            "login": "testuser",
            "password": "Testpass_422!"
        }
        
        response = requests.post(LOGIN_URL, json=login_test_data)
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Login with test user successful!")
            user_info = data.get('user', {})
            return {
                "user_id": user_info.get('id'),
                "login": user_info.get('login'),
                "token": f"test_token_{user_info.get('id')}"
            }
        else:
            print(f"Login with test user failed: {response.text}")

    except Exception as e:
        print(f"Auth test error: {e}")
    
    return None

if __name__ == "__main__":
    test_auth()