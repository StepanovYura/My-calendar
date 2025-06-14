from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.models import User
from datetime import timedelta

active_sessions = {}  # В памяти сервера - плохо TODO сделать выход из профиля через блэклист токенов 

class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        
        # Валидация
        required_fields = ['email', 'password', 'name']
        if not all(field in data for field in required_fields):
            return {"error": "Необходимы email, пароль и имя"}, 400
            
        if User.query.filter_by(email=data['email']).first():
            return {"error": "Пользователь с таким email уже существует"}, 400

        # Создание пользователя
        user = User(
            email=data['email'],
            name=data['name'],
            password_hash=generate_password_hash(data['password']),
            privacy_setting=data.get('privacy_setting', 'all')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Генерация токена
        token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=30)
        )
        
        return {
            "message": "Пользователь создан",
            "token": token,
            "user_id": user.id
        }, 201

class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return {"error": "Требуется email и пароль"}, 400
            
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return {"error": "Неверный email или пароль"}, 401
            
        token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=30)
        )

        active_sessions[user.id] = True

        return {
            "token": token,
            "user_id": user.id,
            "is_admin": user.role == 'admin'
        }

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        # В реальном приложении нужно добавить токен в blacklist
        user_id = int(get_jwt_identity())
        active_sessions[user_id] = False

        return {"message": "Успешный выход из системы"}
    
class CheckAuth(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        
        return {
            "authenticated": True,
            "user_id": user.id,
            "is_admin": user.role == 'admin',
            # 'user': user
        }