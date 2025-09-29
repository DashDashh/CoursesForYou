from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from enum import Enum
from sqlalchemy import Enum as SQLEnum
from extensions import db

class statusType(Enum):
    NOT_BEGIN = 0
    UNCORRECT = 1
    DONE = 2

class User_progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    step_id = db.Column(db.Integer, db.ForeignKey('step.id'), nullable=False)
    status = db.Column(SQLEnum(statusType), nullable=False)
    num_tries = db.Column(db.Integer, nullable=False, info = {'check': 'num_trie > 0'})
    date_last = db.Column(DateTime)