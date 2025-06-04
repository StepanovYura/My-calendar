from api.notifications import notify_friend_request, notify_friend_request_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import Friend, User
from flask_restful import Resource
from flask import request
from extensions import db

# Отправка запроса на дружбу
class FriendRequest(Resource): 
    @jwt_required()
    def post(self):
        data = request.get_json()
        receiver_id = data.get('user_id')
        
        if not receiver_id:
            return {"error": "Не указан пользователь"}, 400
            
        if receiver_id == int(get_jwt_identity()):
            return {"error": "Нельзя добавить себя в друзья"}, 400
            
        receiver = db.session.get(User, receiver_id)
        if not receiver:
            return {"error": "Пользователь не найден"}, 404
            
        # Проверяем существующую заявку
        existing_request = Friend.query.filter(
            ((Friend.sender_id == int(get_jwt_identity())) & (Friend.receiver_id == receiver_id)) |
            ((Friend.sender_id == receiver_id) & (Friend.receiver_id == int(get_jwt_identity())))
        ).first()
        
        if existing_request:
            if existing_request.status == 'pending':
                return {"error": "Запрос уже отправлен"}, 400
            if existing_request.status == 'accepted':
                return {"error": "Пользователь уже у вас в друзьях"}, 400

        # Создаем новую заявку
        friend_request = Friend(
            sender_id=int(get_jwt_identity()),
            receiver_id=receiver_id,
            status='pending'
        )
        db.session.add(friend_request)
        db.session.commit()
        
        # Отправляем уведомление
        notify_friend_request(receiver_id)
        
        return {"message": "Запрос на дружбу отправлен"}

# Ответ на запрос дружбы (принять/отклонить)
class FriendResponse(Resource):
    @jwt_required()
    def post(self, request_id):
        data = request.get_json()
        action = data.get('action')  # кнопка 'accept' или 'decline'
        
        if action not in ['accept', 'decline']:
            return {"error": "Неверное действие"}, 400
            
        friend_request = db.session.get(Friend, request_id)
        if not friend_request:
            return {"error": "Запрос не найден"}, 404
            
        if friend_request.receiver_id != int(get_jwt_identity()):
            return {"error": "Вы не можете ответить на этот запрос"}, 403
            
        if friend_request.status != 'pending':
            return {"error": "Запрос уже обработан"}, 400
            
        if action == 'accept':
            friend_request.status = 'accepted'
            message = "Запрос на дружбу принят"
            
            # Отправляем уведомление отправителю
            notify_friend_request_response(friend_request, True)
        else:
            friend_request.status = 'declined'
            message = "Запрос на дружбу отклонен"

            # Отправляем уведомление отправителю
            notify_friend_request_response(friend_request, False)

        db.session.commit()
        
        
        return {"message": message}

# Список друзей и входящих/исходящих запросов
class FriendList(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        
        # Получаем все связанные записи
        friends = Friend.query.filter(
            ((Friend.sender_id == user_id) | (Friend.receiver_id == user_id))
        ).all()
        
        result = {
            "friends": [],
            "outgoing_requests": [],
            "incoming_requests": []
        }
        
        for f in friends:
            if f.status == 'accepted':
                friend_id = f.receiver_id if f.sender_id == user_id else f.sender_id
                friend = db.session.get(User, friend_id)
                result["friends"].append({
                    "id": friend.id,
                    "name": friend.name,
                    "avatar_url": friend.avatar_url
                })
            elif f.status == 'pending':
                if f.sender_id == user_id:
                    receiver = db.session.get(User, f.receiver_id)
                    result["outgoing_requests"].append({
                        "request_id": f.id,
                        "user_id": receiver.id,
                        "name": receiver.name,
                        "avatar_url": receiver.avatar_url
                    })
                else:
                    sender = db.session.get(User, f.sender_id)
                    result["incoming_requests"].append({
                        "request_id": f.id,
                        "user_id": sender.id,
                        "name": sender.name,
                        "avatar_url": sender.avatar_url
                    })
        
        return result

# Информация о конкретном друге
class FriendDetail(Resource):
    @jwt_required()
    def get(self, friend_id):
        user_id = int(get_jwt_identity())
        
        # Проверяем дружеские отношения
        friendship = Friend.query.filter(
            ((Friend.sender_id == user_id) & (Friend.receiver_id == friend_id)) |
            ((Friend.sender_id == friend_id) & (Friend.receiver_id == user_id)),
            Friend.status == 'accepted'
        ).first()
        
        if not friendship:
            return {"error": "Пользователь не в ваших друзьях"}, 403
            
        friend = db.session.get(User, friend_id)
        if not friend:
            return {"error": "Пользователь не найден"}, 404
            
        return {
            "id": friend.id,
            "name": friend.name,
            "avatar_url": friend.avatar_url,
            "privacy_setting": friend.privacy_setting
        }

# Удаление из друзей
class RemoveFriend(Resource):
    @jwt_required()
    def delete(self, friend_id):
        user_id = int(get_jwt_identity())
        
        friendship = Friend.query.filter(
            ((Friend.sender_id == user_id) & (Friend.receiver_id == friend_id)) |
            ((Friend.sender_id == friend_id) & (Friend.receiver_id == user_id)),
            Friend.status == 'accepted'
        ).first()
        
        if not friendship:
            return {"error": "Пользователь не в ваших друзьях"}, 400
            
        db.session.delete(friendship)
        db.session.commit()
        
        return {"message": "Пользователь удален из друзей"}