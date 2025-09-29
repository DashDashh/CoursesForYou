from flask import Flask
from extensions import db
from models.User import User
from models.Course import Course
from models.Theme import Theme
from models.Module import Module
from models.Step import Step
from models.Theory import Theory
from models.Task import Task
from models.Review import Review
from models.User_progress import User_progress
from models.User_Course import User_Course

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/coursesforyou'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)