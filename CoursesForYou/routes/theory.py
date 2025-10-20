from flask import Blueprint, request, jsonify
from models import Step, Theory
from extensions import db

theory_bp = Blueprint('theory', __name__)

@theory_bp.route('/steps/<int:step_id>/theory', methods=['GET'])
def get_theory(step_id):
    try:
        step = Step.query.get_or_404(step_id)
        theory = Theory.query.filter_by(step_id=step_id).first()
        return jsonify({
            'step_id': step_id,
            'theory_id': theory.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch theory for step'}), 500
    
@theory_bp.route('/steps/<int:step_id>/theory', methods=['POST'])
def create_theory(step_id):
    try:
        data = request.get_json()
        print(f"Received theory data: {data}")
        step = Step.query.get_or_404(step_id)
        print(f"Step found: {step.id}")
        if not data.get('text'):
                print(f"Missing required field: text")
                return jsonify({'error': f'Field text is required'}), 400
        
        print("Creating theory object...")
        theory = Theory(
             step_id = step_id,
             text = data['text']
        )
        print(f"Theory object created")

        db.session.add(theory)
        print("Theory added to session")
        
        db.session.commit()
        print("Changes committed to database")

        return jsonify({
            'message': 'Theory created successfully',
            'theory_id': theory.id,
            'theory': theory.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"EXCEPTION in create_theory: {str(e)}") 
        print(f"Exception type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to create theory'}), 500
    
@theory_bp.route('/theory/<int:theory_id>', methods=['GET'])
def get_theory(theory_id):
    try:
        theory = Theory.query.get_or_404(theory_id)
        return jsonify(theory.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch theory'}), 500
    
@theory_bp.route('/theory/<int:theory_id>', methods=['PUT'])
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
        return jsonify({'error': 'Failed to update step'}), 500
    
