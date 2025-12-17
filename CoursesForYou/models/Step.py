from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from enum import Enum
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import CheckConstraint
from extensions import db

class stepType(Enum):
    THEORY = 1
    TASK = 2

class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id', ondelete='SET NULL'), nullable=False)
    number = db.Column(db.Integer, nullable=False, info={'check': 'number > 0'})
    step_type = db.Column(SQLEnum(stepType), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "(SELECT COUNT(*) FROM theory WHERE theory.step_id = step.id) + "
            "(SELECT COUNT(*) FROM task WHERE task.step_id = step.id) = 1",
            name='exactly_one_child_step'
        ),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'number': self.number,
            'step_type': self.step_type.value
        }