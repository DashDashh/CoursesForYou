from flask import Blueprint, request, jsonify
from models import Course, Theme, User, Review, User_Course
from extensions import db
from models.Course import CourseLevel

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/courses', methods=['POST'])
def create_course():
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        required_fields = ['name', 'theme_id']
        for field in required_fields:
            if not data.get(field):
                print(f"Missing required field: {field}")
                return jsonify({'error': f'Field {field} is required'}), 400
        
        teacher_id = data.get('id_teacher')
        theme_id = data.get('theme_id')
        
        if not teacher_id:
            print("Missing teacher_id")
            return jsonify({'error': 'Teacher ID is required'}), 400
        
        theme = Theme.query.get(theme_id)
        if not theme:
            print(f"Theme with ID {theme_id} not found")
            return jsonify({'error': 'Theme not found'}), 404
        
        teacher = User.query.get(teacher_id)
        if not teacher:
            print(f"Teacher with ID {teacher_id} not found")
            return jsonify({'error': 'Teacher not found'}), 404
        
        print(f"Theme found: {theme.name}")
        print(f"Teacher found: {teacher.login}")
        
        print("Creating course object...")
        level_value = data.get('level', 1)
        if isinstance(level_value, int):
            level_enum = CourseLevel(level_value)
        else:
            level_enum = level_value

        course = Course(
            name=data['name'],
            id_teacher=teacher_id,
            description=data.get('description', ''),
            theme_id=theme_id,
            level=level_enum
        )
        
        print(f"Course object created: {course.name}")
        
        db.session.add(course)
        print("Course added to session")
        
        db.session.commit()
        print("Changes committed to database")
        
        return jsonify({
            'message': 'Course created successfully',
            'course_id': course.id,
            'course': course.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"EXCEPTION in create_course: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Course creation failed'}), 500

@courses_bp.route('/courses', methods=['GET'])
def get_courses():
    try:
        theme_id = request.args.get('theme_id', type=int)
        level = request.args.get('level', type=int)
        teacher_id = request.args.get('teacher_id', type=int)
        
        query = Course.query

        if theme_id:
            query = query.filter(Course.theme_id == theme_id)
        if level:
            level_enum = CourseLevel(level)
            query = query.filter(Course.level == level_enum)
        if teacher_id:
            query = query.filter(Course.id_teacher == teacher_id)
        
        courses = query.all()

        return jsonify({'courses': [course.to_dict() for course in courses]}), 200
    except Exception as e:
        print(f"Error in get_courses: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to fetch courses'}), 500
    
@courses_bp.route('/course/<int:course_id>', methods=['GET'])
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
    
@courses_bp.route('/course/<int:course_id>/reviews', methods=['GET'])
def get_course_reviews(course_id):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        reviews = Review.query.filter_by(course_id=course_id).order_by(Review.date.desc())\
        .paginate(page=page, per_page=per_page, error_out = False)

        return jsonify({
            'reviews': [review.to_dict() for review in reviews.items],
            'total': reviews.total,
            'pages': reviews.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch reviews'}), 500