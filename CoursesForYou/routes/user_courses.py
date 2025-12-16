from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from models import User, Course, User_Course
from extensions import db
from .auth import get_user_from_auth

user_courses_bp = Blueprint('user_courses', __name__)


@user_courses_bp.route('/user/<int:user_id>/courses', methods=['GET'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def get_user_courses(user_id):
    try:
        user = User.query.get_or_404(user_id)

        user_courses = User_Course.query.filter_by(user_id=user_id).all()

        courses_data = []
        for uc in user_courses:
            course = Course.query.get(uc.course_id)
            if course:
                courses_data.append({
                    'course_id': course.id,
                    'course_name': course.name,
                    'progress': uc.progress or 0,
                    'enrolled_date': uc.enrolled_date.isoformat() if uc.enrolled_date else None
                })
        return jsonify(courses_data), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user_course'}), 500


@user_courses_bp.route('/my_courses', methods=['GET'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def get_my_courses():
    try:
        user = get_user_from_auth()
        if not user:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_courses = User_Course.query.filter_by(user_id=user.id).all()
        
        courses_data = []
        for uc in user_courses:
            course = Course.query.get(uc.course_id)
            if course:
                course_dict = course.to_dict()
                
                teacher = User.query.get(course.id_teacher)
                if teacher:
                    course_dict['author'] = teacher.login
                    course_dict['author_display'] = teacher.login_display
                
                
                courses_data.append(course_dict)
        
        return jsonify(courses_data), 200
    except Exception as e:
        print(f"Ошибка получения моих курсов: {e}")
        return jsonify({'error': 'Failed to get my courses'}), 500

@user_courses_bp.route('/course/<int:course_id>/users', methods=['GET'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def get_course_users(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        user_courses = User_Course.query.filter_by(course_id=course_id).all()

        users_data = []
        for uc in user_courses:
            user = User.query.get(uc.user_id)
            if user:
                users_data.append({
                    'user_id': user.id,
                    'login': user.login
                })
        return jsonify(users_data), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch course_user'}), 500


@user_courses_bp.route('/enroll', methods=['POST'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def enroll_in_course():
    try:
        print("=== ЗАПРОС НА ЗАПИСЬ НА КУРС ===")
        
        user = get_user_from_auth()
        if not user:
            print("Пользователь не авторизован")
            return jsonify({'error': 'Not authenticated'}), 401
        
        print(f"Пользователь авторизован: {user.login} (ID: {user.id})")
        
        data = request.get_json()
        print(f"Данные запроса: {data}")
        
        course_id = data.get('course_id')
        if not course_id:
            print("Course ID не указан")
            return jsonify({'error': 'Course ID is required'}), 400
        
        course = Course.query.get(course_id)
        if not course:
            print(f"Курс с ID {course_id} не найден")
            return jsonify({'error': 'Course not found'}), 404
        
        print(f"Курс найден: {course.name} (ID: {course.id})")
        
        existing_enrollment = User_Course.query.filter_by(
            user_id=user.id, 
            course_id=course_id
        ).first()
        
        if existing_enrollment:
            print(f"Пользователь уже записан на этот курс")
            return jsonify({'error': 'You are already enrolled in this course'}), 409
        
        user_course = User_Course(
            user_id=user.id,
            course_id=course_id
        )
        
        db.session.add(user_course)
        db.session.commit()
        
        print(f"Пользователь {user.login} успешно записан на курс {course.name}")
        
        return jsonify({'message': 'Successfully enrolled in course'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка записи на курс: {e}")
        import traceback
        print(f"TRACEBACK: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to enroll in course'}), 500

@user_courses_bp.route('/user/<int:user_id>/course/<int:course_id>', methods=['POST'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def create_user_course(user_id, course_id):
    try:
        user = User.query.get_or_404(user_id)
        course = Course.query.get_or_404(course_id)

        existing_enrollment = User_Course.query.filter_by(
            user_id=user_id, 
            course_id=course_id
        ).first()

        if existing_enrollment:
            return jsonify({
                'message': 'User is already enrolled in this course',
                'enrollment_id': existing_enrollment.id
            }), 409
        
        new_enrollment = User_Course(
            user_id=user_id,
            course_id=course_id
        )

        db.session.add(new_enrollment)
        db.session.commit()

        return jsonify({
            'message': 'Successfully enrolled in course',
            'enrollment_id': new_enrollment.id,
            'user_id': user_id,
            'course_id': course_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to enroll in course',
            'message': str(e)
        }), 500


@user_courses_bp.route('/user/<int:user_id>/course/<int:course_id>', methods=['DELETE'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def delete_user_course(user_id, course_id):
    try:
        User.query.get_or_404(user_id)
        Course.query.get_or_404(course_id)

        existing_enrollment = User_Course.query.filter_by(
                user_id=user_id, 
                course_id=course_id
            ).first()
        
        if not existing_enrollment:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        db.session.delete(existing_enrollment)
        db.session.commit()
        return jsonify({'message': 'Enrollment deleted successfully.'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to delete enrollment'}), 500