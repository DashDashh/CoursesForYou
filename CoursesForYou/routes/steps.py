from flask import Blueprint, request, jsonify
from models import Module, Step, Theory, Task
from extensions import db
from models.Step import stepType

steps_bp = Blueprint('steps', __name__)

@steps_bp.route('/modules/<int:module_id>/steps', methods=['GET'])
def get_steps(module_id):
    try:
        module = Module.query.get_or_404(module_id)
        steps = Step.query.filter_by(module_id=module_id).order_by(Step.number.asc()).all()
        return jsonify({
            'module_id': module_id,
            'module_name': module.name,
            'steps': [step.to_dict() for step in steps]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch steps for module'}), 500
    
@steps_bp.route('/modules/<int:module_id>/steps', methods=['POST'])
def create_step(module_id):
    try:
        data = request.get_json()
        print(f"Received step data: {data}")

        module = Module.query.get_or_404(module_id)
        print(f"Module found: {module.name}")

        required_fields = ['number', 'step_type']
        for field in required_fields:
            if not data.get(field):
                print(f"Missing required field: {field}")
                return jsonify({'error': f'Field {field} is required'}), 400
        
        step_type_value = data['step_type']
        try:
            if isinstance(step_type_value, int):
                step_type_enum = stepType(step_type_value)
            elif isinstance(step_type_value, str):
                step_type_enum = stepType[step_type_value.upper()]
            else:
                raise ValueError("step_type must be integer or string")
        except (ValueError, KeyError) as e:
            print(f"Invalid step_type: {step_type_value}")
            return jsonify({'error': f'step_type must be 1(THEORY) or 2(TASK)'}), 400
        
        existing_step = Step.query.filter_by(
            module_id=module_id,
            number=data['number']
        ).first()

        if existing_step:
            print(f"Step with number {data['number']} already exists")
            return jsonify({'error': 'Step with this number already exists in the module'}), 409
        
        print("Creating step object...")

        step = Step(
            module_id=module_id,
            number=data['number'],
            step_type=step_type_enum
        )

        print(f"Step object created")
        
        db.session.add(step)
        print("Step added to session")
        
        db.session.commit()
        print("Changes committed to database")

        return jsonify({
            'message': 'Step created successfully',
            'step_id': step.id,
            'step': step.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"EXCEPTION in create_step: {str(e)}") 
        print(f"Exception type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to create step'}), 500
    
@steps_bp.route('/steps/<int:step_id>', methods=['GET'])
def get_step(step_id):
    try:
        step = Step.query.get_or_404(step_id)
        return jsonify(step.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch step'}), 500
    
@steps_bp.route('/steps/<int:step_id>', methods=['PUT'])
def update_step(step_id):
    try:
        step = Step.query.get_or_404(step_id)
        data = request.get_json()

        if 'number' in data:
            if data['number'] != step.number:
                existing = Step.query.filter_by(
                    module_id=step.module_id, 
                    number=data['number']
                ).first()
                if existing:
                    return jsonify({'error': 'Step with this number already exists'}), 409
            step.number = data['number']
        
        if 'step_type' in data:
            step_type_value = data['step_type']
            try:
                if isinstance(step_type_value, int):
                    step.step_type = stepType(step_type_value)
                elif isinstance(step_type_value, str):
                    step.step_type = stepType[step_type_value.upper()]
                else:
                    raise ValueError("step_type must be integer or string")
            except (ValueError, KeyError) as e:
                return jsonify({'error': f'step_type must be 1(THEORY) or 2(TASK)'}), 400
        
        db.session.commit()
        return jsonify({
            'message': 'Step updated successfully',
            'step': step.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update step'}), 500
    
@steps_bp.route('/steps/<int:step_id>', methods=['DELETE'])
def delete_step(step_id):
    try:
        step = Step.query.get_or_404(step_id)
        # if step.step_type == 1:
        #     theory = Theory.get_or_404(step_id)
        #     db.session.delete(theory)
        #     db.session.commit()
        # else:
        #     task = Task.query.get_or_404(step_id)
        #     db.session.delete(task)
        #     db.session.commit()


        db.session.delete(step)
        db.session.commit()

        return jsonify({'message': 'Step deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete step'}), 500