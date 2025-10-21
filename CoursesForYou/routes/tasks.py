from flask import Blueprint, request, jsonify
from models import Task, Step
from extensions import db

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        return jsonify(task.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch task'}), 500

@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        data = request.get_json()

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
        return jsonify({'error': 'Failed to update task'}), 500

@tasks_bp.route('/steps/<int:step_id>/task', methods=['GET'])
def get_task_by_step(step_id):
    try:
        task = Task.query.filter_by(step_id=step_id).first()
        if not task:
            return jsonify({'error': 'Task not found for this step'}), 404
            
        return jsonify(task.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch task'}), 500

@tasks_bp.route('/tasks/<int:task_id>/check-answer', methods=['POST'])
def check_answer(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        data = request.get_json()
        
        if not data.get('answer'):
            return jsonify({'error': 'Answer is required'}), 400
        
        user_answer = data.get('answer', '').strip()
        correct_answer = task.answer.strip()
        
        is_correct = user_answer.lower() == correct_answer.lower()
        
        return jsonify({
            'is_correct': is_correct,
            'correct_answer': correct_answer if not is_correct else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to check answer'}), 500