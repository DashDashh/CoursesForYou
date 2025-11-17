from flask import Blueprint, request, jsonify
from models import User, Course, Module, Step, User_progress
from models.User_progress import statusType
from flask_cors import cross_origin
from extensions import db
from datetime import datetime, timezone

user_progresses_bp = Blueprint('user_progress', __name__)

@user_progresses_bp.route('/user/<int:user_id>/step/<int:step_id>', methods=['POST', 'PUT'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def update_step_progress(user_id, step_id):
    try:
        user = User.query.get_or_404(user_id)
        step = Step.query.get_or_404(step_id)

        data = request.get_json()
        status_str = data.get('status')

        try:
            status_enum = statusType[status_str] if status_str else statusType.NOT_BEGIN
        except KeyError:
            return jsonify({'error': 'Invalid status. Use: NOT_BEGIN, UNCORRECT, DONE'}), 400
        
        progress = User_progress.query.filter_by(
            user_id=user_id, 
            step_id=step_id
        ).first()

        if progress:
            progress.status = status_enum
            progress.num_tries = progress.num_tries + 1
            progress.date_last = datetime.now(timezone.utc)
        else:
            progress = User_progress(
                user_id=user_id,
                step_id=step_id,
                status=status_enum,
                num_tries=0,
                date_last=datetime.now(timezone.utc)
            )
            db.session.add(progress)

        db.session.commit()

        return jsonify({
            'message': 'Progress updated successfully',
            'progress_id': progress.id,
            'status': progress.status.name,
            'num_tries': progress.num_tries,
            'date_last': progress.date_last.isoformat() if progress.date_last else None
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@user_progresses_bp.route('/user/<int:user_id>/course/<int:course_id>', methods=['GET'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def get_course_progress(user_id, course_id):
    try:
        modules = Module.query.filter_by(course_id=course_id).all()

        course_progress = {
            'course_id': course_id,
            'total_steps': 0,
            'completed_steps': 0,
            'in_progress_steps': 0,
            'not_started_steps': 0,
            'progress_percentage': 0
        }

        for module in modules:
            steps = Step.query.filter_by(module_id=module.id).all()
            course_progress['total_steps'] += len(steps)

            for step in steps:
                progress = User_progress.query.filter_by(
                    user_id = user_id,
                    step_id = step.id
                ).first()

                if progress:
                    if progress.status == statusType.DONE:
                        course_progress['completed_steps'] += 1
                    elif progress.status == statusType.UNCORRECT:
                        course_progress['in_progress_steps'] += 1
                    else:
                        course_progress['not_started_steps'] += 1

        if course_progress['total_steps'] > 0:
            course_progress['progress_percentage'] = round(course_progress['completed_steps'] / course_progress['total_steps'] * 100, 2)
            
        return jsonify(course_progress), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@user_progresses_bp.route('/user/<int:user_id>/module/<int:module_id>', methods=['GET'])
@cross_origin(origins=["http://localhost:5500", "http://127.0.0.1:5500"], supports_credentials=True)
def get_module_progress(user_id, module_id):
    try:
        print(f"DEBUG: Starting get_module_progress for user {user_id}, module {module_id}")
        
        user = User.query.get_or_404(user_id)
        print(f"DEBUG: User found: {user.id}")
        
        module = Module.query.get_or_404(module_id)
        print(f"DEBUG: Module found: {module.id}, name: {getattr(module, 'name', 'NO_NAME_FIELD')}")
        
        steps = Step.query.filter_by(module_id=module_id).all()
        print(f"DEBUG: Found {len(steps)} steps for module {module_id}")

        module_progress = {
            'module_id': module_id,
            'module_name': getattr(module, 'name', 'Unknown'),
            'total_steps': len(steps),
            'completed_steps': 0,
            'in_progress_steps': 0,
            'not_started_steps': 0,
            'steps': []
        }

        for i, step in enumerate(steps):
            print(f"DEBUG: Processing step {i+1}/{len(steps)}: id={step.id}, type={getattr(step, 'step_type', 'NO_TYPE')}")
            
            progress = User_progress.query.filter_by(
                user_id=user_id, 
                step_id=step.id
            ).first()
            
            if progress:
                status = progress.status
                print(f"DEBUG: Progress found for step {step.id}: status={status}, tries={progress.num_tries}")
            else:
                status = statusType.NOT_BEGIN
                print(f"DEBUG: No progress found for step {step.id}, using NOT_BEGIN")
            
            if status == statusType.DONE:
                module_progress['completed_steps'] += 1
            elif status == statusType.UNCORRECT:
                module_progress['in_progress_steps'] += 1
            else:
                module_progress['not_started_steps'] += 1
            
            step_data = {
                'step_id': step.id,
                'step_type': step.step_type.name if hasattr(step.step_type, 'name') else str(step.step_type),  # ← ИСПРАВЛЕНО
                'status': status.name,
                'num_tries': progress.num_tries if progress else 0,
                'last_updated': progress.date_last.isoformat() if progress and progress.date_last else None
            }
            module_progress['steps'].append(step_data)

        print(f"DEBUG: Successfully built module progress")
        return jsonify(module_progress), 200
        
    except Exception as e:
        print(f"ERROR in get_module_progress: {str(e)}")
        import traceback
        print(f"TRACEBACK: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

