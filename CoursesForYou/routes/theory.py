from flask import Blueprint, request, jsonify
from models import Theory, Step
from extensions import db

theories_bp = Blueprint('theories', __name__)

@theories_bp.route('/theories/<int:theory_id>', methods=['GET'])
def get_theory(theory_id):
    try:
        theory = Theory.query.get_or_404(theory_id)
        return jsonify(theory.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch theory'}), 500

@theories_bp.route('/theories/<int:theory_id>', methods=['PUT'])
def update_theory(theory_id):
    try:
        theory = Theory.query.get_or_404(theory_id)
        data = request.get_json()

        if 'text' in data:
            theory.text = data['text']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Theory updated successfully',
            'theory': theory.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update theory'}), 500

@theories_bp.route('/steps/<int:step_id>/theory', methods=['GET'])
def get_theory_by_step(step_id):
    try:
        theory = Theory.query.filter_by(step_id=step_id).first()
        if not theory:
            return jsonify({'error': 'Theory not found for this step'}), 404
            
        return jsonify(theory.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch theory'}), 500