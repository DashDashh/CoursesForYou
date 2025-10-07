from flask import Blueprint, request, jsonify
from models import Theme
from extensions import db

themes_bp = Blueprint('themes', __name__)

@themes_bp.route('/themes', methods=['POST'])
def create_theme():
    try:
        data = request.get_json()
        
        required_fields = ['name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Field {field} is required'}), 400
            
        theme = Theme(
            name=data['name']
        )
        db.session.add(theme)
        db.session.commit()

        return jsonify({
            'message': 'Theme created successfully',
            'theme_id': theme.id,
            'theme': theme.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Theme creation failed'}), 500
    

@themes_bp.route('/themes', methods=['GET'])
def get_themes():
    try:
        name = request.args.get('name', type=str)
        query = Theme.query

        if name:
            query = query.filter(Theme.name == name)

        themes = query.all()

        return jsonify({'themes': [theme.to_dict() for theme in themes]}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch themes'}), 500
    
@themes_bp.route('/theme/<int:theme_id>', methods=['GET'])
def get_theme(theme_id):
    try:
        theme = Theme.query.get_or_404(theme_id)
        theme_data = theme.to_dict()
        return jsonify(theme_data), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch course'}), 500