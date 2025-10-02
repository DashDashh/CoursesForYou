from extensions import db
from .User import User
from .Course import Course
from .Theme import Theme
from .Module import Module
from .Step import Step
from .Theory import Theory
from .Task import Task
from .Review import Review
from .User_progress import User_progress
from .User_Course import User_Course

__all__ = [
    'User', 'Course', 'Theme', 'Module', 'Step', 
    'Theory', 'Task', 'Review', 'User_progress', 'User_Course'
]

def create_tables():
    db.create_all()
    print("Все таблицы созданы!")
    

    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Таблицы в базе: {tables}")