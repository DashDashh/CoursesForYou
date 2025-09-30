from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from enum import Enum
from sqlalchemy import Enum as SQLEnum
from extensions import db
from validators import validate_login, validate_password, get_password_strength
from werkzeug.security import generate_password_hash, check_password_hash

class roleType(Enum):
    ADMIN = 1
    USER = 2

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(SQLEnum(roleType), nullable=False, default=roleType.USER)
    login = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    register_date = db.Column(DateTime, default=lambda: datetime.now(timezone.utc))
    avatar_path = db.Column(db.String(255), default='') # добавить дефолт картинку
    about = db.Column(db.String(255))
    password_changed_date = db.Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint("LENGTH(login) >= 3 AND LENGTH(login) <= 20", name='check_login_length'),
        db.CheckConstraint("LENGTH(password) >= 60", name='check_password_hash_length'),
    )
    
    def __init__(self, **kwargs):
        if 'login' in kwargs:
            self.set_login(kwargs['login'])
        
        if 'password' in kwargs:
            self.set_password(kwargs['password'])
        
        for key, value in kwargs.items():
            if key not in ['login', 'password']:
                setattr(self, key, value)
    
    def set_login(self, login):
        if not validate_login(login):
            raise ValueError(
                "Login must be 3-20 characters, only Latin letters, numbers, _ . -"
            )
        
        existing_user = User.query.filter_by(login=login).first()
        if existing_user and existing_user.id != self.id:
            raise ValueError("This login is already taken")
        
        self.login = login
    
    def set_password(self, password):
        is_valid, errors = validate_password(password)
        if not is_valid:
            raise ValueError("Password validation failed: " + "; ".join(errors))
        
        strength = get_password_strength(password)
        if strength < 3:
            raise ValueError("Password is too weak. Use uppercase, lowercase, numbers and special characters")
        
        self.password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=16
        )
        self.password_changed_date = datetime.now(timezone.utc)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def is_password_old(self, days=90):
        if not self.password_changed_date:
            return True
        delta = datetime.now(timezone.utc) - self.password_changed_date
        return delta.days > days
    
    def get_password_strength_info(self):
        return {
            'strength': 'strong',
            'changed_date': self.password_changed_date,
            'is_old': self.is_password_old()
        }
    
    @property
    def login_display(self):
        return f"@{self.login}" if self.login else ""
    
    @classmethod
    def get_by_login(cls, login):
        return cls.query.filter_by(login=login).first()
    
    @classmethod
    def create_user(cls, login, password, **kwargs):
        user = cls(login=login, password=password, **kwargs)
        return user