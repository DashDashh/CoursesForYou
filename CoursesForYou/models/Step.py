from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from enum import Enum
from sqlalchemy import Enum as SQLEnum
from extensions import db

class stepType(Enum):
    THEORY = 1
    TASK = 2

class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    number = db.Column(db.Integer, nullable=False, info={'check': 'number > 0'})
    step_type = db.Column(SQLEnum(stepType), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'number': self.number,
            'step_type': self.step_type.value
        }