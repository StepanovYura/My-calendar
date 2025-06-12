from flask import request
from extensions import db
from flask_restful import Resource
from datetime import datetime, date
from flask_login import current_user, login_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.notifications import notify_event_participants, notify_added_to_event
from models.models import Event, EventParticipant, User, Friend

#--------------------------GET_методы---------------------------

# Запрос своих событий или событий друга по дням/неделям/месяцам 
class UserEvents(Resource):
    @jwt_required()
    def get(self):
        # 1. Определяем пользователя, чьи события надо получить
        user_id = request.args.get("user_id", type=int)

        if user_id is None:
            user_id = int(get_jwt_identity())  # свои события
        else:
            if user_id != int(get_jwt_identity()):
                # Проверка, является ли запрошенный пользователь другом
                friend = db.session.query(Friend).filter(
                    ((Friend.sender_id == int(get_jwt_identity())) & (Friend.receiver_id == user_id) |
                    (Friend.sender_id == user_id) & (Friend.receiver_id == int(get_jwt_identity()))) &
                    (Friend.status == 'accepted')
                ).first()

                if not friend:
                    return {"error": "Вы не можете просматривать события этого пользователя."}, 403

                # Проверка приватности
                target_user = db.session.get(User, user_id)
                if not target_user or target_user.privacy_setting != 'all':
                    return {"error": "Этот пользователь ограничил доступ к своим событиям."}, 403

        # 2. Фильтрация событий
        query = db.session.query(Event).join(EventParticipant).filter(
            EventParticipant.user_id == user_id
        )

        # 3. Фильтры по дате
        def parse_range(param_from, param_to):
            try:
                start = datetime.strptime(request.args.get(param_from), "%Y-%m-%d")
                end = datetime.strptime(request.args.get(param_to), "%Y-%m-%d")
                return datetime.combine(start, datetime.min.time()), datetime.combine(end, datetime.max.time())
            except:
                return None, None

        if request.args.get("date"):
            try:
                day = datetime.strptime(request.args.get("date"), "%Y-%m-%d")
                start = datetime.combine(day.date(), datetime.min.time())
                end = datetime.combine(day.date(), datetime.max.time())
                query = query.filter(Event.date_time >= start, Event.date_time <= end)
            except:
                return {"error": "Неверный формат параметра date"}, 400

        elif request.args.get("week_start") and request.args.get("week_end"):
            start, end = parse_range("week_start", "week_end")
            if not start:
                return {"error": "Неверный формат дат недели"}, 400
            query = query.filter(Event.date_time >= start, Event.date_time <= end)

        elif request.args.get("month_start") and request.args.get("month_end"):
            start, end = parse_range("month_start", "month_end")
            if not start:
                return {"error": "Неверный формат дат месяца"}, 400
            query = query.filter(Event.date_time >= start, Event.date_time <= end)

        events = query.all()

        return [{
            "id": e.id,
            "group_id": e.group_id,
            "title": e.title,
            "description": e.description,
            "date_time": e.date_time.isoformat(),
            "duration_minutes": e.duration_minutes,
            "event_type": e.event_type,
            "status": e.status,
        } for e in events]

# Запрос конкретного события 
class EventDetail(Resource):
    @jwt_required()
    def get(self, event_id):
        event = db.session.get(Event, event_id)
        user = db.session.get(User, int(get_jwt_identity()))

        if not event:
            return {"error": "Событие не найдено"}, 404

        # Проверка участия пользователя
        is_participant = db.session.query(EventParticipant).filter_by(
            event_id=event_id,
            user_id=int(get_jwt_identity())
        ).first()

        if not is_participant and user.role != 'admin':
            return {"error": "Вы не являетесь участником этого события"}, 403

        return [{
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "date_time": e.date_time.isoformat(),
            "duration_minutes": e.duration_minutes,
            "status": e.status,
            "group_id": e.group_id,
            "event_draft_id": e.event_draft_id,
            "created_at": e.created_at.isoformat(),
            "created_by": e.created_by,
            "event_type": e.event_type,
            "color": e.color
        } for e in event]


# Для Администраторов запрос всех событий
class AllEvents(Resource):
    @jwt_required()
    def get(self):
        user = db.session.get(User, int(get_jwt_identity()))

        if user.role != 'admin':
            return {"error": "Доступ запрещён. Только для администраторов."}, 403

        events = Event.query.all()
        return [{
            'id': e.id,
            'title': e.title,
            'description': e.description,
            'date_time': e.date_time.isoformat(),
            'duration_minutes': e.duration_minutes,
            'status': e.status
        } for e in events]
    
# Получение всех участников события
class EventParticipants(Resource):
    @jwt_required()
    def get(self, event_id):
        # Проверяем, что пользователь имеет доступ к событию
        is_participant = db.session.query(EventParticipant).filter_by(
            event_id=event_id,
            user_id=int(get_jwt_identity())
        ).first()

        if not is_participant:
            return {"error": "Вы не являетесь участником этого события"}, 403

        # Получаем всех участников события с их данными
        participants = db.session.query(
            EventParticipant,
            User
        ).join(
            User, EventParticipant.user_id == User.id
        ).filter(
            EventParticipant.event_id == event_id
        ).all()

        return [{
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "role": user.role,
            "privacy_setting": user.privacy_setting,
        } for participant, user in participants]
    
#--------------------------PUT/DELETE_методы---------------------------

class EventEditor(Resource):
    @jwt_required()
    def put(self, event_id):
        event = db.session.get(Event, event_id)
        user = db.session.get(User, int(get_jwt_identity()))

        if not event:
            return {"error": "Событие не найдено"}, 404

        # Проверка, можно ли редактировать (создатель или админ)
        if user.id != event.created_by and user.role != 'admin':
            return {"error": "Недостаточно прав для редактирования"}, 403

        data = request.get_json()
        if not data:
            return {"error": "Пустой запрос"}, 400
        
        event.title = data.get("title", event.title)
        event.description = data.get("description", event.description)
        event.date_time = datetime.fromisoformat(data["date_time"]) if data.get("date_time") else event.date_time
        event.duration_minutes = data.get("duration_minutes", event.duration_minutes)
        event.status = data.get("status", event.status)

        # Оповещение остальным пользователям об изменении
        notify_event_participants(event, f"Событие '{event.title}' было обновлено.", type='update')

        db.session.commit()
        return {"message": "Событие обновлено успешно"}

    @jwt_required()
    def delete(self, event_id):
        event = db.session.get(Event, event_id)
        user = db.session.get(User, int(get_jwt_identity()))

        if not event:
            return {"error": "Событие не найдено"}, 404

        # Проверка, можно ли удалять (создатель или админ)
        if user.id != event.created_by and user.role != 'admin':
            return {"error": "Недостаточно прав для удаления"}, 403

        # Оповещение остальным пользователям об изменении
        notify_event_participants(event, f"Событие '{event.title}' было удалено.", type='update')

        db.session.delete(event)
        db.session.commit()
        return {"message": "Событие удалено"}


#--------------------------POST_методы---------------------------

class EventCreate(Resource):
    @jwt_required()
    def post(self):
        data = request.json
        new_event = Event(
            title=data["title"],
            description=data.get("description", ""),
            date_time=datetime.fromisoformat(data["date_time"]),
            duration_minutes=data.get("duration_minutes", 60),
            status=data.get("status", "active"),
            created_by=int(get_jwt_identity())
        )
        db.session.add(new_event)
        db.session.flush() # получим event.id до коммита

        # Добавить текущего пользователя как участника
        participant = EventParticipant(user_id=int(get_jwt_identity()), event_id=new_event.id)
        db.session.add(participant)

        # Если указан друг
        friend_username = data.get("friend_username")
        if friend_username:
            friend_user = User.query.filter_by(name=friend_username).first()
            if not friend_user:
                db.session.rollback()
                return {"message": "Пользователь с таким никнеймом не найден"}, 404

            # Проверка дружбы
            friendship = Friend.query.filter(
                ((Friend.sender_id == int(get_jwt_identity())) & (Friend.receiver_id == friend_user.id)) |
                ((Friend.sender_id == friend_user.id) & (Friend.receiver_id == int(get_jwt_identity()))),
                Friend.status == 'accepted'
            ).first()

            if not friendship:
                    db.session.rollback()
                    return {"message": "Пользователь не является вашим другом"}, 403
            
            # Добавляем друга в участники
            db.session.add(EventParticipant(user_id=friend_user.id, event_id=new_event.id))

            notify_added_to_event(new_event.id, friend_user.id)

        db.session.commit()
        return {"message": "Событие создано", "id": new_event.id}


class EventAddParticipant(Resource):
    @jwt_required()
    def post(self, event_id):
        data = request.get_json()
        friend_username = data.get("username")
        if not friend_username:
            return {"error": "Не указано имя пользователя"}, 400

        user = db.session.get(User, int(get_jwt_identity()))
        event = db.session.get(Event, event_id)

        if not event:
            return {"error": "Событие не найдено"}, 404

        # Проверка прав
        if user.id != event.created_by and user.role != 'admin':
            return {"error": "Недостаточно прав"}, 403

        # Ищем пользователя-друга
        friend = db.session.query(User).filter_by(name=friend_username).first()
        if not friend:
            return {"error": "Пользователь не найден"}, 404

        # Проверка: уже добавлен?
        exists = db.session.query(EventParticipant).filter_by(
            event_id=event_id,
            user_id=friend.id
        ).first()

        if exists:
            return {"message": "Пользователь уже участвует в событии"}

        # Добавляем друга
        participant = EventParticipant(event_id=event_id, user_id=friend.id)
        db.session.add(participant)
        db.session.commit()

        return {"message": f"Пользователь {friend.name} добавлен к событию"}
