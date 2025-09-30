from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from extensions import db
from validators import validate_theme_name

class Theme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    
    __table_args__ = (
        db.CheckConstraint("LENGTH(name) >= 2 AND LENGTH(name) <= 20", name='check_theme_name_length'),
    )
    
    def __init__(self, **kwargs):
        if 'name' in kwargs:
            self.set_name(kwargs['name'])
        
        for key, value in kwargs.items():
            if key != 'name':
                setattr(self, key, value)
    
    def set_name(self, name):
        name = ' '.join(name.strip().split())
        
        if not validate_theme_name(name):
            raise ValueError(
                "Название темы должно:\n"
                "• Содержать только кириллические буквы\n"
                "• Начинаться с заглавной буквы\n"
                "• Содержать 2-20 символов\n"
                "• После пробела/дефиса должна быть заглавная буква\n"
                "• Пример: 'Программирование', 'Веб-Разработка'"
            )
        
        existing_theme = Theme.query.filter_by(name=name).first()
        if existing_theme and existing_theme.id != self.id:
            raise ValueError(f"Тема '{name}' уже существует")
        
        self.name = name
    
    def capitalize_name(self):
        if self.name:
            words = []
            for word in self.name.split():
                if '-' in word:
                    hyphenated_words = [w.capitalize() for w in word.split('-')]
                    words.append('-'.join(hyphenated_words))
                else:
                    words.append(word.capitalize())
            self.name = ' '.join(words)
    
    @classmethod
    def create_theme(cls, name):
        theme = cls(name=name)
        return theme
    
    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter(cls.name.ilike(name)).first()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }