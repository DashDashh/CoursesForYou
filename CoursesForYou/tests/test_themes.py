import requests
import json

BASE_URL = "http://localhost:5000"
THEMES_URL = f"{BASE_URL}/api/themes"

def test_themes():
    print("Testing themes API...")
    
    test_theme_name = "Программирование"
    
    try:
        print("\n1. Testing GET all themes...")
        response = requests.get(THEMES_URL)
        print(f"Get themes status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            themes = data.get('themes', [])
            print(f"Found {len(themes)} themes")
            for theme in themes:
                print(f"   - {theme.get('name')} (ID: {theme.get('id')})")
        else:
            print(f"Get themes failed: {response.text}")
        
        print("\n2. Testing POST theme...")
        theme_data = {
            "name": test_theme_name
        }
        
        response = requests.post(THEMES_URL, json=theme_data)
        print(f"Create theme status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            theme_id = data.get('theme_id')
            print(f"Theme created successfully!")
            print(f"   Theme: {data.get('theme', {}).get('name')} (ID: {theme_id})")
            
            created_theme_id = theme_id
        else:
            print(f"Create theme failed: {response.text}")
            response = requests.get(THEMES_URL, params={"name": test_theme_name})
            if response.status_code == 200:
                data = response.json()
                themes = data.get('themes', [])
                if themes:
                    created_theme_id = themes[0].get('id')
                    print(f"Theme already exists, using ID: {created_theme_id}")
                else:
                    created_theme_id = 1
            else:
                created_theme_id = 1
            return None
        
        print("\n3. Testing GET theme by ID...")
        theme_url = f"{BASE_URL}/api/theme/{created_theme_id}"
        response = requests.get(theme_url)
        print(f"Get theme by ID status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Theme retrieved successfully!")
            print(f"   Name: {data.get('name')}, ID: {data.get('id')}")
        else:
            print(f"Get theme by ID failed: {response.text}")
        
        print("\n4. Testing theme search by name...")
        response = requests.get(THEMES_URL, params={"name": test_theme_name})
        print(f"Search theme status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            themes = data.get('themes', [])
            print(f"Found {len(themes)} themes with name '{test_theme_name}'")
            for theme in themes:
                print(f"   - {theme.get('name')} (ID: {theme.get('id')})")
        else:
            print(f"Search theme failed: {response.text}")
        
    except Exception as e:
        print(f"Themes test error: {e}")
        return None

def test_theme_validation():
    print("\nTesting theme name validation...")
    
    test_cases = [
        {"name": "Математика", "should_work": True, "description": "Корректное название"},
        {"name": "математика", "should_work": False, "description": "Маленькая первая буква"},
        {"name": "Web Development", "should_work": False, "description": "Латинские буквы"},
        {"name": "Программирование123", "should_work": False, "description": "Цифры в названии"},
        {"name": "Ф", "should_work": False, "description": "Слишком короткое"},
        {"name": "Очень Длинное Название Тема", "should_work": False, "description": "Слишком длинное"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  {i}. {test_case['description']}: '{test_case['name']}'")
        
        try:
            response = requests.post(THEMES_URL, json={"name": test_case['name']})
            
            if test_case['should_work'] and response.status_code == 201:
                print("     PASS - Theme created as expected")
            elif not test_case['should_work'] and response.status_code != 201:
                print("     PASS - Theme properly rejected")
            elif test_case['should_work'] and response.status_code != 201:
                print(f"     FAIL - Should have worked but got {response.status_code}: {response.text}")
            else:
                print(f"     FAIL - Should have been rejected but got {response.status_code}")
                
        except Exception as e:
            print(f"     ERROR: {e}")

if __name__ == "__main__":
    test_themes()
    test_theme_validation()