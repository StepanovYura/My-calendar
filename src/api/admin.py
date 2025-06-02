from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.models import User
from functools import wraps

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        if not user or user.role != 'admin':
            return {"error": "Требуются права администратора"}, 403
        return f(*args, **kwargs)
    return wrapper

class AdminUserList(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        users = User.query.all()
        
        return [{
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "privacy_setting": u.privacy_setting,
            "role": u.role
        } for u in users]

class AdminUserActions(Resource):
    @jwt_required()
    @admin_required
    def put(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "Пользователь не найден"}, 404
            
        data = request.get_json()
        
        # Обновляем все допустимые поля
        allowed_fields = ['name', 'email', 'role', 'avatar_url', 'privacy_setting']
        
        # Особые проверки для email
        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                return {"error": "Email уже занят"}, 400
        
        for field in allowed_fields:
            if field in data:  # Если поле есть в запросе
                user.field = data[field]  
        
        
        db.session.commit()
        
        return {"message": "Пользователь обновлен"}
    
    @jwt_required()
    @admin_required
    def delete(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "Пользователь не найден"}, 404
            
        if user.role == 'admin':
            return {"error": "Нельзя удалить администратора"}, 403
            
        db.session.delete(user)
        db.session.commit()
        
        return {"message": "Пользователь удален"}