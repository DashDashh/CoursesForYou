import requests
import json

BASE_URL = "http://localhost:5000"

REVIEWS_URL = f"{BASE_URL}/api/reviews"

def test_reviews(course_id, user_id):
    print("Testing reviews API...")

    print("\n1. Testing create review...")

    review_data = {
        "user_id": user_id,
        "text": "Отличный курс! Очень понятное объяснение материала."
    }
    response = requests.post(f"{REVIEWS_URL}/course/{course_id}", json=review_data)
    print(f"Create review status: {response.status_code}")

    if response.status_code == 201:
        data = response.json()
        review_id = data['review']['id']
        print(f"Review created successfully: ID={review_id}")

    print("\n2. Testing get course reviews...")
    response = requests.get(f"{REVIEWS_URL}/course/{course_id}")
    print(f"Get course reviews status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total']} reviews for course {course_id}")
        print(f"   Pages: {data['pages']}, Current page: {data['current_page']}")
        if data['reviews']:
            print(f"   First review: '{data['reviews'][0]['text'][:50]}...'")

    print("\n3. Testing get specific review...")
    response = requests.get(f"{REVIEWS_URL}/{review_id}")
    print(f"Get review status: {response.status_code}")

    if response.status_code == 200:
            review_data = response.json()
            print(f"Review found: '{review_data['text'][:50]}...'")

    print("\n4. Testing delete review...")
    response = requests.delete(f"{REVIEWS_URL}/{review_id}")
    print(f"Delete review status: {response.status_code}")

    if response.status_code == 200:
            print("Review deleted successfully")

    

