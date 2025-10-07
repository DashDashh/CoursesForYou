from app import app, db
from models import User, Course, Theme, Module, Step, Theory, Task, Review, User_progress, User_Course

def clear_database():
    with app.app_context():
        try:
            print("Начинаю очистку базы данных...")
            
            User_progress.query.delete()
            User_Course.query.delete()
            Review.query.delete()
            Theory.query.delete()
            Task.query.delete()
            Step.query.delete()
            Module.query.delete()
            Course.query.delete()
            Theme.query.delete()
            User.query.delete()
            
            db.session.commit()
            
            print("Все таблицы успешно очищены!")
                
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при очистке базы: {e}")

if __name__ == "__main__":
    clear_database()