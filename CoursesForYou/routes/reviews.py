from flask import Blueprint, request, jsonify
from models import User, Course, Review
from models.User_progress import statusType
from flask_cors import cross_origin
from extensions import db
from datetime import datetime, timezone

reviews_bp = Blueprint('reviews', __name__)

# Добавьте этот маршрут для создания отзывов
@reviews_bp.route('/reviews', methods=['POST', 'OPTIONS'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def create_review():
    try:
        # Обработка preflight запроса
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
            
        data = request.get_json()

        if not data or 'user_id' not in data or 'text' not in data or 'course_id' not in data:
            return jsonify({'error': 'Missing required fields: user_id, course_id and text'}), 400
        
        user_id = data.get('user_id')
        course_id = data.get('course_id')
        text = data.get('text').strip()

        # Проверяем существование пользователя и курса
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        if not text:
            return jsonify({'error': 'Review text cannot be empty'}), 400
        
        new_review = Review(
            user_id=user_id,
            course_id=course_id,
            text=text,
            date=datetime.now(timezone.utc)
        )

        db.session.add(new_review)
        db.session.commit()
        
        return jsonify({
            'message': 'Review created successfully',
            'review': new_review.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create review: {str(e)}'}), 500

# Остальные маршруты остаются без изменений
@reviews_bp.route('/reviews/course/<int:course_id>', methods=['GET'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
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
    
@reviews_bp.route('/reviews/<int:review_id>', methods=['GET'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def get_review(review_id):
    try:
        review = Review.query.get_or_404(review_id)
        return jsonify(review.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch review'}), 500
    
@reviews_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@cross_origin(origins=["https://localhost:5500", "https://127.0.0.1:5500",
                       "http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def delete_review(review_id):
    try:
        review = Review.query.get_or_404(review_id)
        db.session.delete(review)
        db.session.commit()

        return jsonify({'message': 'Review deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete review: {str(e)}'}), 500