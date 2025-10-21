from test_db import test_db
from test_auth import test_auth  
from test_courses import test_courses
from test_themes import test_themes 
from test_modules import test_modules
from test_steps import test_steps
from test_theory_tasks import test_theories_tasks

if __name__ == "__main__":
    print("Starting tests...")
    
    test_db()
    
    test_themes()
    
    token = test_auth()
    
    if token:
        test_courses(token)
    else:
        test_courses(None)
    
    test_modules(5)
    test_steps()
    test_theories_tasks(3, 4)