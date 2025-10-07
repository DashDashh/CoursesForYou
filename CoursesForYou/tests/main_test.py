from test_db import test_db
from test_auth import test_auth  
from test_courses import test_courses
from test_themes import test_themes 

if __name__ == "__main__":
    print("Starting tests...")
    
    test_db()
    
    test_themes()
    
    token = test_auth()
    
    if token:
        test_courses(token)
    else:
        test_courses(None)