import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import app, db
from models.User import User
from models.Course import Course
from models.Module import Module
from werkzeug.security import generate_password_hash

def test_db():
    with app.app_context():
        print("Testing database connection...")
        
        try:
            db.create_all()
            print("Tables created successfully")
            
            test_user = User(
                login="testuser",
                password="Testpass_422!"
            )
            
            db.session.add(test_user)
            db.session.commit()
            print("Test user created successfully")
            print(f"Login: testuser, Password: Testpass_422!")
            
            user = User.query.filter_by(login="testuser").first()
            if user:
                print(f"User found: {user.login}, ID: {user.id}")
            else:
                print("User not found!")
                
        except Exception as e:
            print(f"Database error: {e}")

if __name__ == "__main__":
    test_db()