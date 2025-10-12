from flask import Blueprint, request, jsonify
from models import Course, Module
from extensions import db

modules_bp = Blueprint('modules', __name__)

@modules_bp.route('/courses/<int:course_id>/modules', methods=['GET'])
def get_modules(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        modules = Module.query.filter_by(course_id=course_id).order_by(Module.number.asc()).all()
        return jsonify({
            'course_id': course_id,
            'course_name': course.name,
            'modules': [module.to_dict() for module in modules]
        }), 200
    except Exception as e:
        return jsonify({'error' : 'Failed to fetch modules for course'}), 500
    
@modules_bp.route('/courses/<int:course_id>/modules', methods=['POST'])
def create_module(course_id):
    try:
        data = request.get_json()
        print(f"Received module data: {data}")
        
        course = Course.query.get(course_id)
        if not course:
            print(f"Course with ID {course_id} not found")
            return jsonify({'error': 'Course not found'}), 404
        
        print(f"Course found: {course.name}")
        
        required_fields = ['name', 'number']
        for field in required_fields:
            if not data.get(field):
                print(f"Missing required field: {field}")
                return jsonify({'error': f'Field {field} is required'}), 400
        
        existing_module = Module.query.filter_by(
            course_id=course_id, 
            number=data['number']
        ).first()
        
        if existing_module:
            print(f"Module with number {data['number']} already exists")
            return jsonify({'error': 'Module with this number already exists in the course'}), 409
        
        print("Creating module object...")
        
        module = Module(
            course_id=course_id,
            number=data['number'],
            name=data['name']
        )
        
        print(f"Module object created: {module.name}")
        
        db.session.add(module)
        print("Module added to session")
        
        db.session.commit()
        print("Changes committed to database")
        
        return jsonify({
            'message': 'Module created successfully',
            'module_id': module.id,
            'module': module.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"EXCEPTION in create_module: {str(e)}") 
        print(f"Exception type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to create module'}), 500
    
@modules_bp.route('/modules/<int:module_id>', methods=['GET'])
def get_module(module_id):
    try:
        module = Module.query.get_or_404(module_id)
        return jsonify(module.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch module'}), 500
    
@modules_bp.route('/modules/<int:module_id>', methods=['PUT'])
def update_module(module_id):
    try:
        module = Module.query.get_or_404(module_id)
        data = request.get_json()
        
        if 'name' in data:
            module.name = data['name']
        if 'number' in data:
            if data['number'] != module.number:
                existing = Module.query.filter_by(
                    course_id=module.course_id, 
                    number=data['number']
                ).first()
                if existing:
                    return jsonify({'error': 'Module with this number already exists'}), 409
            module.number = data['number']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Module updated successfully',
            'module': module.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update module'}), 500
        
@modules_bp.route('/modules/<int:module_id>', methods=['DELETE'])
def delete_module(module_id):
    try:
        module = Module.query.get_or_404(module_id)
        
        db.session.delete(module)
        db.session.commit()
        
        return jsonify({'message': 'Module deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete module'}), 500