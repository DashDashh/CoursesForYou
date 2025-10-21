from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from extensions import db

class Theory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    step_id = db.Column(db.Integer, db.ForeignKey('step.id', ondelete='CASCADE'), nullable=False)
    text = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'step_id': self.step_id,
            'text': self.text
        }