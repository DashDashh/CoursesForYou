from flask import Flask
from extensions import db
from models import User, Course, Theme, Module, Step, Theory, Task, Review, User_progress, User_Course
from routes import auth

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/coursesforyou'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    db.init_app(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Все таблицы созданы успешно!")
    app.run(debug=True)