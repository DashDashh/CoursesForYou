from flask import Flask
from extensions import db
from config import config
from flask_cors import CORS
import os
import ssl

from routes.auth import auth_bp
from routes.courses import courses_bp
from routes.themes import themes_bp
from routes.modules import modules_bp
from routes.steps import steps_bp
from routes.theory import theories_bp
from routes.tasks import tasks_bp
from routes.user_courses import user_courses_bp
from routes.user_progresses import user_progresses_bp
from routes.reviews import reviews_bp
from routes.users import users_bp
from routes.admin import admin_bp

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)

    CORS(app, 
         origins=["https://localhost:5500", "https://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:5500"],
         supports_credentials=True,
         methods=["GET", "POST", "PUT", "DELETE"],
         allow_headers=["Content-Type", "Authorization"])
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(courses_bp, url_prefix='/api')
    app.register_blueprint(themes_bp, url_prefix='/api')
    app.register_blueprint(modules_bp, url_prefix='/api')
    app.register_blueprint(steps_bp, url_prefix='/api')
    app.register_blueprint(theories_bp, url_prefix='/api')
    app.register_blueprint(tasks_bp, url_prefix='/api')
    app.register_blueprint(user_courses_bp, url_prefix='/api')
    app.register_blueprint(user_progresses_bp, url_prefix='/api/user_progress')
    app.register_blueprint(reviews_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    
    return app

app = create_app('development')

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
    
    cert_path = os.path.join('ssl', 'cert.pem')
    key_path = os.path.join('ssl', 'key.pem')

    if os.path.exists(cert_path) and os.path.exists(key_path):
        print("Сертификаты найдены, запускаем HTTPS сервер...")
        print(f"Сертификат: {cert_path}")
        print(f"Ключ: {key_path}")
        
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert_path, key_path)
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            ssl_context=ssl_context  # HTTPS!
        )
    else:
        print("Сертификаты не найдены!")
        print("Запуск HTTP сервера...")
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
    