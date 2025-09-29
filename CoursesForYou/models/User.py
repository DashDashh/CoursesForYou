from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from enum import Enum
from sqlalchemy import Enum as SQLEnum
from extensions import db

class roleType(Enum):
    ADMIN = 1
    USER = 2

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(SQLEnum(roleType), nullable=False)
    login = db.Column(db.String(20), unique=True, nullable=False) #Ограничения написать
    password = db.Column(db.String(60), nullable=False) #Ограничения и разобраться с хешированием
    register_date = db.Column(DateTime, default=lambda: datetime.now(timezone.utc))
    avatar_path = db.Column(db.String(255), default='') #добавить путь к дефолт картинке
    about = db.Column(db.String(255))
