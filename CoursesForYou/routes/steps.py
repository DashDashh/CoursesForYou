from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from models import Module, Step, Theory, Task
from extensions import db
from models.Step import stepType

steps_bp = Blueprint('steps', __name__)

@steps_bp.route('/modules/<int:module_id>/steps', methods=['OPTIONS'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], 
              supports_credentials=True,
              methods=['GET', 'POST', 'OPTIONS'],
              allow_headers=['Content-Type', 'Authorization'])
def handle_steps_options(module_id):
    return jsonify({}), 200

@steps_bp.route('/modules/<int:module_id>/steps', methods=['GET'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], 
              supports_credentials=True,
              methods=['GET'],
              allow_headers=['Content-Type', 'Authorization'])
def get_steps(module_id):
    try:
        module = Module.query.get_or_404(module_id)
        steps = Step.query.filter_by(module_id=module_id).order_by(Step.number.asc()).all()
        
        steps_data = []
        for step in steps:
            step_data = step.to_dict()
            
            if step.step_type == stepType.THEORY:
                theory = Theory.query.filter_by(step_id=step.id).first()
                step_data['theory'] = theory.to_dict() if theory else None
            elif step.step_type == stepType.TASK:
                task = Task.query.filter_by(step_id=step.id).first()
                step_data['task'] = task.to_dict() if task else None
            
            steps_data.append(step_data)
        
        return jsonify({
            'module_id': module_id,
            'module_name': module.name,
            'steps': steps_data
        }), 200
    except Exception as e:
        print(f"Error in get_steps: {str(e)}")
        return jsonify({'error': 'Failed to fetch steps for module'}), 500
    
@steps_bp.route('/modules/<int:module_id>/steps', methods=['POST'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], 
              supports_credentials=True,
              methods=['POST'],
              allow_headers=['Content-Type', 'Authorization'])
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

        db.session.add(step)
        db.session.flush()
        
        if step_type_enum == stepType.THEORY:
            theory_text = (data.get('theory_text') or 
                          data.get('text') or 
                          data.get('theory', {}).get('text', ''))
            
            print(f"Theory text from data: {theory_text}")
            
            if not theory_text:
                return jsonify({'error': 'Theory text is required'}), 400
                
            theory = Theory(
                step_id=step.id,
                text=theory_text
            )
            db.session.add(theory)
            print("Theory created")
            
        elif step_type_enum == stepType.TASK:
            task_question = (data.get('task_question') or 
                           data.get('question') or 
                           data.get('task', {}).get('question', ''))
            
            correct_answer = (data.get('correct_answer') or 
                            data.get('answer') or 
                            data.get('task', {}).get('answer', ''))
            
            print(f"Task question: {task_question}, answer: {correct_answer}")
            
            if not task_question or not correct_answer:
                return jsonify({'error': 'Task question and answer are required'}), 400
                
            task = Task(
                step_id=step.id,
                question=task_question,
                answer=correct_answer
            )
            db.session.add(task)
            print("Task created")
        
        db.session.commit()
        print("Changes committed to database")

        step_data = step.to_dict()
        if step_type_enum == stepType.THEORY:
            theory = Theory.query.filter_by(step_id=step.id).first()
            step_data['theory'] = theory.to_dict() if theory else None
        elif step_type_enum == stepType.TASK:
            task = Task.query.filter_by(step_id=step.id).first()
            step_data['task'] = task.to_dict() if task else None

        return jsonify({
            'message': 'Step created successfully',
            'step_id': step.id,
            'step': step_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"EXCEPTION in create_step: {str(e)}") 
        print(f"Exception type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to create step'}), 500

@steps_bp.route('/steps/<int:step_id>', methods=['OPTIONS'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], 
              supports_credentials=True,
              methods=['GET', 'PUT', 'DELETE', 'OPTIONS'],
              allow_headers=['Content-Type', 'Authorization'])
def handle_step_options(step_id):
    return jsonify({}), 200
    
@steps_bp.route('/steps/<int:step_id>', methods=['GET'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], 
              supports_credentials=True,
              methods=['GET'],
              allow_headers=['Content-Type', 'Authorization'])
def get_step(step_id):
    try:
        step = Step.query.get_or_404(step_id)
        step_data = step.to_dict()
        
        if step.step_type == stepType.THEORY:
            theory = Theory.query.filter_by(step_id=step_id).first()
            step_data['theory'] = theory.to_dict() if theory else None
        elif step.step_type == stepType.TASK:
            task = Task.query.filter_by(step_id=step_id).first()
            step_data['task'] = task.to_dict() if task else None
        
        return jsonify(step_data), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch step'}), 500
    
@steps_bp.route('/steps/<int:step_id>', methods=['PUT'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], 
              supports_credentials=True,
              methods=['PUT'],
              allow_headers=['Content-Type', 'Authorization'])
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
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], 
              supports_credentials=True,
              methods=['DELETE'],
              allow_headers=['Content-Type', 'Authorization'])
def delete_step(step_id):
    try:
        step = Step.query.get_or_404(step_id)
        print(f"Deleting step {step_id} of type {step.step_type}")
        if step.step_type == stepType.THEORY:
            theory = Theory.query.filter_by(step_id=step_id).first()
            if theory:
                print(f"Deleting theory record {theory.id}")
                db.session.delete(theory)
                db.session.flush()
        elif step.step_type == stepType.TASK:
            task = Task.query.filter_by(step_id=step_id).first()
            if task:
                print(f"Deleting task record {task.id}")
                db.session.delete(task)
                db.session.flush()
        
        print(f"Deleting step {step_id}")
        db.session.delete(step)
        db.session.commit()

        print("Step deleted successfully")
        return jsonify({'message': 'Step deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"EXCEPTION in delete_step: {str(e)}") 
        print(f"Exception type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to delete step'}), 500
    

@steps_bp.route('/theory/<int:step_id>', methods=['PUT'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], 
              supports_credentials=True,
              methods=['PUT'],
              allow_headers=['Content-Type', 'Authorization'])
def update_theory(step_id):
    try:
        data = request.get_json()
        print(f"Updating theory for step {step_id}: {data}")

        theory = Theory.query.filter_by(step_id=step_id).first()
        if not theory:
            return jsonify({'error': 'Theory not found'}), 404

        if 'text' in data:
            theory.text = data['text']

        db.session.commit()

        return jsonify({
            'message': 'Theory updated successfully',
            'theory': theory.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error updating theory: {str(e)}")
        return jsonify({'error': 'Failed to update theory'}), 500

@steps_bp.route('/task/<int:step_id>', methods=['PUT'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], 
              supports_credentials=True,
              methods=['PUT'],
              allow_headers=['Content-Type', 'Authorization'])
def update_task(step_id):
    try:
        data = request.get_json()
        print(f"Updating task for step {step_id}: {data}")

        task = Task.query.filter_by(step_id=step_id).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        if 'question' in data:
            task.question = data['question']
        if 'answer' in data:
            task.answer = data['answer']

        db.session.commit()

        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error updating task: {str(e)}")
        return jsonify({'error': 'Failed to update task'}), 500

@steps_bp.route('/theory/<int:step_id>', methods=['OPTIONS'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], 
              supports_credentials=True,
              methods=['PUT', 'OPTIONS'],
              allow_headers=['Content-Type', 'Authorization'])
def handle_theory_options(step_id):
    return jsonify({}), 200

@steps_bp.route('/task/<int:step_id>', methods=['OPTIONS'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], 
              supports_credentials=True,
              methods=['PUT', 'OPTIONS'],
              allow_headers=['Content-Type', 'Authorization'])
def handle_task_options(step_id):
    return jsonify({}), 200