from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from enum import Enum
from sqlalchemy import Enum as SQLEnum
from extensions import db

class CourseLevel(Enum):
    BEGINNER = 1
    ELEMENTARY = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    id_teacher = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(255))
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'), nullable=False)
    level = db.Column(SQLEnum(CourseLevel), nullable=False,default=CourseLevel.BEGINNER)