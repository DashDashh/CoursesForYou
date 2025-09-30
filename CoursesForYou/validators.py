import re
from typing import Tuple, List

def validate_login(login):
    if not login or not isinstance(login, str):
        return False
    
    if len(login) < 3 or len(login) > 20:
        return False
    
    if not re.match(r'^[a-zA-Z0-9_.\-]+$', login):
        return False
    
    if login.startswith(('.', '-')) or login.endswith(('.', '-')):
        return False
    
    if '..' in login or '--' in login or '__' in login:
        return False
    
    reserved_logins = {'admin', 'root', 'support', 'system', 'test'}
    if login.lower() in reserved_logins:
        return False
    
    return True


def validate_password(password) -> Tuple[bool, List[str]]:
    errors = []
    
    if not password or not isinstance(password, str):
        errors.append("Password must be a string")
        return False, errors
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if len(password) > 128:
        errors.append("Password cannot exceed 128 characters")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    weak_passwords = {
        'password', 'password123', '12345678', 'qwerty', 'admin', 
        'letmein', 'welcome', 'monkey', 'abc123', '111111'
    }
    if password.lower() in weak_passwords:
        errors.append("This password is too common and insecure")
    
    if re.search(r'(.)\1{2,}', password):
        errors.append("Password cannot contain 3 or more identical characters in a row")
    
    if re.search(r'(abc|bcd|cde|def|123|234|345|456)', password.lower()):
        errors.append("Password cannot contain simple sequences")
    
    return len(errors) == 0, errors

def validate_password_simple(password):
    is_valid, _ = validate_password(password)
    return is_valid

def get_password_strength(password):
    if not password:
        return 0
    
    score = 0
    
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    
    if re.search(r'[a-z]', password) and re.search(r'[A-Z]', password):
        score += 1
    
    if re.search(r'[0-9]', password):
        score += 1
    
    if re.search(r'[^a-zA-Z0-9]', password):
        score += 1
    
    return min(score, 4)


def validate_theme_name(name):
    if not name or not isinstance(name, str):
        return False
    
    if len(name) < 2 or len(name) > 20:
        return False
    
    if not re.match(r'^[А-ЯЁ]', name):
        return False
    
    if not re.match(r'^[А-ЯЁ][а-яёА-ЯЁ\s\-]*$', name):
        return False
    
    if re.search(r'[\s\-][а-яё]', name):
        return False
    
    if re.search(r'\s\s|--', name):
        return False
    
    return True