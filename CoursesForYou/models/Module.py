from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from extensions import db

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    number = db.Column(db.Integer, nullable=False, info={'check': 'number > 0'})
    name = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'number': self.number,
            'name': self.name
        }