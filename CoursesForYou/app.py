from flask import Flask
from extensions import db
from config import config
from sqlalchemy import text

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    return app

app = create_app('development')

if __name__ == '__main__':
    with app.app_context():
        
        try:
            db.session.execute(text('SELECT 1'))
        except Exception as e:
            print(f"Ошибка подключения к PostgreSQL: {e}")
            exit()
        
        try:
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
        except Exception as e:
            print(f"Ошибка импорта моделей: {e}")
            exit()
        
        try:
            db.create_all()
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
            exit()
        
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"Таблицы в PostgreSQL ({len(tables)} шт.):")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("Таблицы не созданы")
                
        except Exception as e:
            print(f"Ошибка при проверке таблиц: {e}")
        
    app.run(debug=True)