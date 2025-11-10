from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from models import Course, Theme, User, Review
from extensions import db
from models.Course import CourseLevel

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/courses', methods=['POST'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
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
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def get_courses():
    try:
        print("=== НАЧАЛО get_courses ===")
        
        from models.Course import Course
        from models.User import User
        from models.User_Course import User_Course
        
        courses = Course.query.all()
        print(f"Найдено курсов: {len(courses)}")
        
        courses_data = []
        for course in courses:
            print(f"Обрабатываем курс: {course.name} (ID: {course.id})")
            
            course_dict = course.to_dict()
            course_dict['title'] = course.name
            course_dict['students_count'] = 0
            course_dict['rating'] = 'нет оценок'
            
            teacher = User.query.get(course.id_teacher)
            if teacher:
                course_dict['author'] = teacher.login
                course_dict['author_display'] = teacher.login_display
                print(f"   Преподаватель: {teacher.login} (ID: {teacher.id})")
            else:
                course_dict['author'] = 'Неизвестный преподаватель'
                course_dict['author_display'] = 'Неизвестный преподаватель'
                print(f"   Преподаватель с ID {course.id_teacher} не найден!")
            
            students_count = User_Course.query.filter_by(course_id=course.id).count()
            course_dict['students_count'] = students_count
            print(f"   Студентов: {students_count}")
            
            courses_data.append(course_dict)
        
        print(f"Успешно обработано {len(courses_data)} курсов")
        return jsonify(courses_data), 200
        
    except Exception as e:
        print(f"ОШИБКА: {e}")
        import traceback
        print(f"TRACEBACK: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to fetch courses: {str(e)}'}), 500


@courses_bp.route('/courses/search', methods=['GET'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def search_courses():
    try:
        search_term = request.args.get('q', '')
        
        if not search_term:
            return jsonify([]), 200
        
        courses = Course.query.filter(
            (Course.name.ilike(f'%{search_term}%')) | 
            (Course.description.ilike(f'%{search_term}%'))
        ).all()
        
        courses_data = []
        for course in courses:
            course_dict = course.to_dict()
            
            teacher = User.query.get(course.id_teacher)
            if teacher:
                course_dict['author'] = teacher.login
                course_dict['author_display'] = teacher.login_display
            
            from models.User_Course import User_Course
            students_count = User_Course.query.filter_by(course_id=course.id).count()
            course_dict['students_count'] = students_count
            
            courses_data.append(course_dict)
        
        return jsonify(courses_data), 200
    except Exception as e:
        print(f"Ошибка поиска курсов: {e}")
        return jsonify({'error': 'Failed to search courses'}), 500


@courses_bp.route('/course/<int:course_id>', methods=['GET'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def get_course(course_id):
    try:
        course = Course.query.get_or_404(course_id)

        teacher = User.query.get(course.id_teacher)
        theme = Theme.query.get(course.theme_id)

        from models.User_Course import User_Course
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
    

@courses_bp.route('/course/<int:course_id>', methods=['PUT'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def update_course(course_id):
    try:
        data = request.get_json()
        print(f"Обновление курса {course_id}: {data}")
        
        course = Course.query.get_or_404(course_id)
        
        # Обновляем поля
        if 'name' in data:
            course.name = data['name']
        if 'description' in data:
            course.description = data['description']
        if 'theme_id' in data:
            course.theme_id = data['theme_id']
        if 'level' in data:
            level_enum = CourseLevel(data['level'])
            course.level = level_enum
        
        db.session.commit()
        
        return jsonify({
            'message': 'Course updated successfully',
            'course': course.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка обновления курса: {e}")
        return jsonify({'error': f'Course update failed: {str(e)}'}), 500