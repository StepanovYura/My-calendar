from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.models import User

class UserProfile(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "privacy_setting": user.privacy_setting,
            "role": user.role
        }

    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        data = request.get_json()
        
        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                return {"error": "Email уже занят"}, 400
            user.email = data['email']
        
        if 'name' in data:
            user.name = data['name']
        
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        
        if 'privacy_setting' in data:
            user.privacy_setting = data['privacy_setting']
        
        db.session.commit()
        
        return {"message": "Профиль обновлен"}

class ChangePassword(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return {"error": "Требуется текущий и новый пароль"}, 400
            
        if not check_password_hash(user.password_hash, data['current_password']):
            return {"error": "Неверный текущий пароль"}, 401
            
        user.password_hash = generate_password_hash(data['new_password'])
        db.session.commit()
        
        return {"message": "Пароль успешно изменен"}

class DeleteAccount(Resource):
    @jwt_required()
    def delete(self):
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        
        db.session.delete(user)
        db.session.commit()
        
        return {"message": "Аккаунт удален"}

class UserSearch(Resource):
    @jwt_required()
    def get(self):
        query = request.args.get('q', '')
            
        users = User.query.filter(
            (User.name.ilike(f'%{query}%')) | 
            (User.email.ilike(f'%{query}%'))
        ).all()
        
        return [{
            "id": u.id,
            "name": u.name,
            "avatar_url": u.avatar_url
        } for u in users]