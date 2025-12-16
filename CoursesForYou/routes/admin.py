from flask import Blueprint, request, jsonify
from models import User, Course, Review, Theme, User_progress, User_Course
from extensions import db
from flask_cors import cross_origin

admin_bp = Blueprint('admin', __name__)

# Проверка прав администратора
def check_admin():
    # Реализуйте проверку прав администратора
    # (зависит от вашей системы аутентификации)
    return True

# Темы
@admin_bp.route('/themes', methods=['GET'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def get_themes():
    if not check_admin():
        return jsonify({'error': 'Access denied'}), 403
    try:
        themes = Theme.query.all()
        return jsonify([{'id': theme.id, 'name': theme.name} for theme in themes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/themes', methods=['POST'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def create_theme():
    if not check_admin():
        return jsonify({'error': 'Access denied'}), 403
    try:
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            return jsonify({'error': 'Theme name is required'}), 400
        
        theme = Theme(name=name)
        db.session.add(theme)
        db.session.commit()
        
        return jsonify({'message': 'Theme created', 'theme': {'id': theme.id, 'name': theme.name}}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/themes/<int:theme_id>', methods=['DELETE'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def delete_theme(theme_id):
    if not check_admin():
        return jsonify({'error': 'Access denied'}), 403
    try:
        theme = Theme.query.get_or_404(theme_id)
        db.session.delete(theme)
        db.session.commit()
        return jsonify({'message': 'Theme deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Пользователи
@admin_bp.route('/users/all', methods=['GET'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def get_all_users():
    if not check_admin():
        return jsonify({'error': 'Access denied'}), 403
    try:
        users = User.query.all()
        return jsonify([{
            'id': user.id,
            'login': user.login,
            'role': user.role.value,
            'register_date': user.register_date.isoformat() if user.register_date else None,
            'is_banned': getattr(user, 'is_banned', False)
        } for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/users/<int:user_id>/toggle-ban', methods=['POST'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def toggle_user_ban(user_id):
    if not check_admin():
        return jsonify({'error': 'Access denied'}), 403
    try:
        user = User.query.get_or_404(user_id)
        # Переключаем статус блокировки
        user.is_banned = not getattr(user, 'is_banned', False)
        db.session.commit()
        return jsonify({'message': 'User status updated', 'is_banned': user.is_banned}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def admin_delete_user(user_id):
    if not check_admin():
        return jsonify({'error': 'Access denied'}), 403
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Статистика
@admin_bp.route('/admin/stats', methods=['GET'])
def get_stats():
    if not check_admin():
        return jsonify({'error': 'Access denied'}), 403
    try:
        total_users = User.query.count()
        total_courses = Course.query.count()
        total_reviews = Review.query.count()
        banned_users = User.query.filter_by(is_banned=True).count() if hasattr(User, 'is_banned') else 0
        
        return jsonify({
            'total_users': total_users,
            'total_courses': total_courses,
            'total_reviews': total_reviews,
            'banned_users': banned_users
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# В admin.py добавьте:
@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not check_admin():
        return jsonify({'error': 'Access denied'}), 403
    try:
        user = User.query.get_or_404(user_id)
        user_login = user.login
        
        # Удаляем связанные данные
        User_progress.query.filter_by(user_id=user_id).delete()
        User_Course.query.filter_by(user_id=user_id).delete()
        Review.query.filter_by(user_id=user_id).delete()
        
        # Удаляем пользователя
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': f'User {user_login} deleted successfully',
            'deleted_user_id': user_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500