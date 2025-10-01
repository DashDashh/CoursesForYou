from flask import Blueprint, request, jsonify
from models import Course, Theme, User, Review, User_Course
from extensions import db

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/courses', methods=['GET'])
def get_courses():
    try:
        theme_id = request.args.get('theme_id', type = int)
        level = request.args.get('level', type = int)
        teacher_id = request.args.get('teacher_id', type = int)
        
        query = Course.query

        if theme_id:
            query = query.filter(Course.theme_id == theme_id)
        if level:
            query = query.filter(Course.level.value == level)
        if teacher_id:
            query = query.filter(Course.teacher_id == teacher_id)
        
        courses = query.all()

        return jsonify({'courses': [course.to_dict() for course in courses]}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch courses'}), 500
    
@courses_bp.route('/course/<int: course_id>', methods=['GET'])
def get_course(course_id):
    try:
        course = Course.query.get_or_404(course_id)

        teacher = User.query.get(course.id_teacher)
        theme = Theme.query.get(course.theme_id)

        students_count = User_Course.query.filter_by(course_id=course_id).count()

        reviews = Review.query.filter_by(course_id=course_id).limit(5).all()

        course_data = course.to_dict()
        course_data.update({
            'teacher': {
                'id': teacher.id,
                'login': teacher.login,
                'login_display': teacher.login_display,
                'avatar_path': teacher.avatar_path
            },
            'theme': theme.to_dict() if theme else None,
            'students_count': students_count,
            'reviews': [review.to_dict() for review in reviews]
        })
        
        return jsonify(course_data), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch course'}), 500
    
@courses_bp.route('/course/<int: course_id>/reviews', methods=['GET'])
def get_course_reviews(course_id):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        reviews = Review.query.filter_by(course_id=course_id).order_by(Review.date.desc())\
        .paginate(page=page, per_page=per_page, error_out = False)

        return jsonify({
            'reviews': [review.to_dict() for review in reviews],
            'total': reviews.total,
            'pages': reviews.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch reviews'}), 500
    
