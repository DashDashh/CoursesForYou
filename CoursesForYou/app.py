from flask import Flask
from extensions import db
from config import config

# Импортируем все Blueprint
from routes.auth import auth_bp
from routes.courses import courses_bp
from routes.themes import themes_bp
from routes.modules import modules_bp
from routes.steps import steps_bp

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    
    # Регистрируем все Blueprint
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(courses_bp, url_prefix='/api')
    app.register_blueprint(themes_bp, url_prefix='/api')
    app.register_blueprint(modules_bp, url_prefix='/api')
    app.register_blueprint(steps_bp, url_prefix='/api')
    
    return app

app = create_app('development')

# Импорты моделей
with app.app_context():
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Все таблицы созданы!")
    app.run(debug=True)