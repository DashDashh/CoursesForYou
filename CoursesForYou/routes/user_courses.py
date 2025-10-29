from flask import Blueprint, request, jsonify
from models import User, Course, User_Course
from extensions import db

user_courses_bp = Blueprint('user_courses', __name__)

@user_courses_bp.route('/user/<int:user_id>/courses', methods=['GET'])
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
                    'course_name': course.name
                })
        return jsonify(courses_data), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user_course'}), 500
    
@user_courses_bp.route('/course/<int:course_id>/users', methods=['GET'])
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
    
@user_courses_bp.route('/user/<int:user_id>/course/<int:course_id>', methods=['POST'])
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
            user_id = user_id,
            course_id = course_id
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

