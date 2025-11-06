from flask import Blueprint, request, jsonify, session
from flask_cors import cross_origin
from models import User
from extensions import db

auth_bp = Blueprint('auth', __name__)

def get_user_from_auth():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    user_id = auth_header.replace('Bearer ', '').strip()
    try:
        return User.query.get(int(user_id))
    except:
        return None

@auth_bp.route('/register', methods=['POST'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def register():
    try:
        data = request.get_json()
        print("Получены данные регистрации:", data)

        if not data.get('login') or not data.get('password'):
            return jsonify({'error': 'Login and password are required.'}), 400
        
        existing_user = User.query.filter_by(login=data['login']).first()
        if existing_user:
            return jsonify({'error': 'This user is already exists.'}), 409
        
        user = User(
            login = data['login'],
            password = data['password'],
            about = data.get('about', ''),
            avatar_path = data.get('avatar_path', '')
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.id,
            'login': user.login
        }), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed.'}), 500
    

@auth_bp.route('/login', methods=['POST'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def login():
    try:
        data = request.get_json()
        print("Получены данные входа:", data)
        
        if not data.get('login') or not data.get('password'):
            return jsonify({'error': 'Login and password are required.'}), 400
        
        user = User.query.filter_by(login=data['login']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid login or password.'}), 401
        
        session['user_id'] = user.id
        session['user_login'] = user.login
        session['user_role'] = user.role.value

        print(f"Пользователь {user.login} вошел в систему")

        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'login': user.login,
                'role': user.role.value,
                'login_display': user.login_display
            },
            'token': str(user.id)
        }), 200
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Ошибка входа: {e}")
        return jsonify({'error': 'Login failed.'}), 500
    

@auth_bp.route('/logout', methods=['POST'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def logout():
    try:
        session.clear()
        return jsonify({'message': 'Logout successful.'}), 200
    except Exception as e:
        return jsonify({'error': 'Logout failed.'}), 500

@auth_bp.route('/check_auth', methods=['GET'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def check_auth():
    try:
        user = get_user_from_auth()
        if not user and 'user_id' in session:
            user = User.query.get(session['user_id'])
        
        if user:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': user.id,
                    'login': user.login,
                    'role': user.role.value
                }
            }), 200
        else:
            return jsonify({'authenticated': False}), 200
    except Exception as e:
        return jsonify({'error': 'Authentification check failed.'}), 500
    

@auth_bp.route('/change_password', methods=['POST'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def change_password():
    try:
        user = get_user_from_auth()
        if not user:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()

        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        user.set_password(data['new_password'])
        db.session.commit()

        return jsonify({'message': 'Password changed successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Change password is failed'}), 500
    
@auth_bp.route('/update_profile', methods=['PUT'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def update_profile():
    try:
        user = get_user_from_auth()
        if not user:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()

        if 'about' in data:
            user.about = data['about']
        if 'avatar_path' in data:
            user.avatar_path = data['avatar_path']
        
        db.session.commit()

        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Profile update failed'}), 500
    

@auth_bp.route('/user_profile', methods=['GET'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def get_user_profile():
    try:
        user = get_user_from_auth()
        if not user:
            return jsonify({'error': 'Not authenticated'}), 401
        
        return jsonify({
            'login': user.login,
            'about': user.about,
            'avatar_path': user.avatar_path,
            'register_date': user.register_date.isoformat() if user.register_date else None
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get profile'}), 500