from flask import request
from extensions import db
from flask_restful import Resource
from datetime import datetime, date
from flask_login import current_user, login_required
from api.notifications import notify_event_participants
from models.models import Event, EventParticipant, User, Friend

#--------------------------GET_методы---------------------------

# Запрос своих событий или событий друга по дням/неделям/месяцам 
class UserEvents(Resource):
    @login_required
    def get(self):
        # 1. Определяем пользователя, чьи события надо получить
        user_id = request.args.get("user_id", type=int)

        if user_id is None:
            user_id = current_user.id  # свои события
        else:
            if user_id != current_user.id:
                # Проверка, является ли запрошенный пользователь другом
                friend = db.session.query(Friend).filter(
                    ((Friend.sender_id == current_user.id) & (Friend.receiver_id == user_id) |
                     (Friend.sender_id == user_id) & (Friend.receiver_id == current_user.id)) &
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
    @login_required
    def get(self, event_id):
        event = db.session.get(Event, event_id)
        if not event:
            return {"error": "Событие не найдено"}, 404

        # Проверка участия пользователя
        is_participant = db.session.query(EventParticipant).filter_by(
            event_id=event_id,
            user_id=current_user.id
        ).first()

        if not is_participant and current_user.role != 'admin':
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
    @login_required
    def get(self):
        if current_user.role != 'admin':
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
    
#--------------------------PUT/DELETE_методы---------------------------

class EventEditor(Resource):
    @login_required
    def put(self, event_id):
        event = db.session.get(Event, event_id)
        if not event:
            return {"error": "Событие не найдено"}, 404

        # Проверка, можно ли редактировать (создатель или админ)
        if current_user.id != event.created_by and current_user.role != 'admin':
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

    @login_required
    def delete(self, event_id):
        event = db.session.get(Event, event_id)
        if not event:
            return {"error": "Событие не найдено"}, 404

        # Проверка, можно ли удалять (создатель или админ)
        if current_user.id != event.created_by and current_user.role != 'admin':
            return {"error": "Недостаточно прав для удаления"}, 403

        # Оповещение остальным пользователям об изменении
        notify_event_participants(event, f"Событие '{event.title}' было удалено.", type='update')

        db.session.delete(event)
        db.session.commit()
        return {"message": "Событие удалено"}


#--------------------------POST_методы---------------------------

class EventCreate(Resource):
    @login_required
    def post(self):
        data = request.json
        new_event = Event(
            title=data["title"],
            description=data.get("description", ""),
            date_time=datetime.fromisoformat(data["date_time"]),
            duration_minutes=data.get("duration_minutes", 60),
            status=data.get("status", "scheduled"),
            created_by=current_user.id
        )
        db.session.add(new_event)
        db.session.commit()

        # Добавить текущего пользователя как участника
        participant = EventParticipant(user_id=current_user.id, event_id=new_event.id)
        db.session.add(participant)
        db.session.commit()

        return {"message": "Событие создано", "id": new_event.id}
