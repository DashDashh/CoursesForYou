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
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
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
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        from models.Review import Review
        
        reviews_deleted = Review.query.filter_by(user_id=user_id).delete()
        print(f"Deleted {reviews_deleted} reviews for user {user.login}")

        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User {user.login} and their {reviews_deleted} reviews deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Failed to delete user', 'details': str(e)}), 500