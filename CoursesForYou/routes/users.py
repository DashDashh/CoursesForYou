from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from models import User
from extensions import db

users_bp = Blueprint('users', __name__)

@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'login': user.login,
            'login_display': user.login_display,
            'about': user.about,
            'avatar_path': user.avatar_path,
            'register_date': user.register_date.isoformat() if user.register_date else None
        }), 200
    except Exception as e:
        return jsonify({'error': 'User not found'}), 404

@users_bp.route('/users/search', methods=['GET'])
def search_users():
    try:
        login = request.args.get('login')
        if not login:
            return jsonify([]), 200
        
        users = User.query.filter(User.login.ilike(f'%{login}%')).all()
        return jsonify([{
            'id': user.id,
            'login': user.login,
            'login_display': user.login_display,
            'about': user.about,
            'avatar_path': user.avatar_path,
            'register_date': user.register_date.isoformat() if user.register_date else None
        } for user in users]), 200
    except Exception as e:
        return jsonify({'error': 'Search failed'}), 500
    
@users_bp.route('/users/all', methods=['GET'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def get_all_users():
    try:
        users = User.query.all()
        
        user_list = [user.to_dict() for user in users]
        
        return jsonify(user_list), 200
    except Exception as e:
        print(f"Error in get_all_users: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch users', 'details': str(e)}), 500
    
@users_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def delete_user(user_id):
    try:
        
        user = User.query.get_or_404(user_id)
        print(f"Найден пользователь: {user.login} (ID: {user_id})")
        
        from models.Course import Course
        from models.Review import Review
        from models.User_progress import User_progress
        from models.User_Course import User_Course
        from models.Module import Module
        from models.Step import Step
        from models.Theory import Theory
        from models.Task import Task
        
        user_courses = Course.query.filter_by(id_teacher=user_id).all()
        
        for course in user_courses:
            
            modules = Module.query.filter_by(course_id=course.id).all()
            for module in modules:
                steps = Step.query.filter_by(module_id=module.id).all()
                for step in steps:
                    Theory.query.filter_by(step_id=step.id).delete()
                    Task.query.filter_by(step_id=step.id).delete()
                    db.session.delete(step)
                db.session.delete(module)
            
            Review.query.filter_by(course_id=course.id).delete()
            
            User_Course.query.filter_by(course_id=course.id).delete()
            
            User_progress.query.filter_by(user_id=user_id).delete()
            
            db.session.delete(course)
            print(f"   Курс '{course.name}' удалён")
        
        print("\n2. Удаление отзывов пользователя...")
        reviews_deleted = Review.query.filter_by(user_id=user_id).delete()
        print(f"   Удалено отзывов: {reviews_deleted}")
        
        print("\n3. Удаление прогресса пользователя...")
        progresses_deleted = User_progress.query.filter_by(user_id=user_id).delete()
        print(f"   Удалено записей прогресса: {progresses_deleted}")
        
        print("\n4. Удаление подписок пользователя...")
        subscriptions_deleted = User_Course.query.filter_by(user_id=user_id).delete()
        print(f"   Удалено подписок: {subscriptions_deleted}")
        
        print("\n5. Удаление пользователя...")
        db.session.delete(user)
        
        db.session.commit()
        
        print(f"\nПОЛЬЗОВАТЕЛЬ {user.login} УДАЛЁН")
        print("="*50)
        
        return jsonify({
            'success': True,
            'message': f'Пользователь {user.login} удалён',
            'stats': {
                'courses_deleted': len(user_courses),
                'reviews_deleted': reviews_deleted,
                'progresses_deleted': progresses_deleted,
                'subscriptions_deleted': subscriptions_deleted
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"\nОШИБКА УДАЛЕНИЯ: {str(e)}")
        import traceback
        traceback.print_exc()
        
        if "foreign key constraint" in str(e).lower():
            return jsonify({
                'error': 'Не удалось удалить пользователя',
                'details': 'У пользователя есть связанные данные',
                'solution': 'Попробуйте использовать функцию переноса курсов'
            }), 400
        
        return jsonify({'error': f'Failed to delete user: {str(e)}'}), 500