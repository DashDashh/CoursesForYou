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
    
    # Добавьте этот метод to_dict
    def to_dict(self):
        """Преобразует объект User в словарь для JSON сериализации"""
        result = {
            'id': self.id,
            'login': self.login,
            'login_display': self.login_display,
            'avatar_path': self.avatar_path,
            'about': self.about,
            'is_banned': getattr(self, 'is_banned', False),  # Добавляем с проверкой
        }
        
        # Обработка дат
        if self.register_date:
            result['register_date'] = self.register_date.isoformat()
        else:
            result['register_date'] = None
            
        if self.password_changed_date:
            result['password_changed_date'] = self.password_changed_date.isoformat()
        else:
            result['password_changed_date'] = None
        
        # Обработка роли (преобразуем Enum в значение)
        if hasattr(self.role, 'value'):
            result['role'] = self.role.value  # Для Enum получаем числовое значение
        else:
            result['role'] = int(self.role) if self.role is not None else 2
        
        return result
    
    # Также добавьте метод для удобства
    def to_dict_admin(self):
        """Версия для админ-панели с дополнительными полями"""
        user_dict = self.to_dict()
        
        # Добавляем дополнительные поля для админ-панели
        user_dict['is_banned'] = getattr(self, 'is_banned', False)
        user_dict['role_name'] = self.role.name if hasattr(self.role, 'name') else ('ADMIN' if self.role == 1 else 'USER')
        
        return user_dict