from flask import Blueprint, request, jsonify
from models import User

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