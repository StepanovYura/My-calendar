from models.models import Notification, EventParticipant, User, Group, GroupMember, Event, EventDraft
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import current_user, login_required
from flask import current_app, request
from flask_restful import Resource
from extensions import mail, db
from flask_mail import Message

# Общая функция для создания уведомления
def create_notification(receiver_id, message, type, sender_id=None, 
                       event_id=None, group_id=None, event_draft_id=None):
    print(f"Попытка создать уведомление для {receiver_id}")
    notification = Notification(
        receiver_id=receiver_id,
        sender_id=sender_id,
        message=message,
        type=type,
        event_id=event_id,
        group_id=group_id,
        event_draft_id=event_draft_id
    )
    db.session.add(notification)
    print("Уведомление добавлено в сессию")
    # # Отправка email
    # user = db.session.get(User, receiver_id)
    # if user and user.email:
    #     msg = Message(
    #         subject="Новое уведомление",
    #         sender=current_app.config['MAIL_USERNAME'],
    #         recipients=[user.email],
    #         body=message
    #     )
    #     mail.send(msg) # либо закоментить либо исправлять, подробности в app.py
    
    db.session.commit()
    print("Уведомление сохранено в БД")

# 1. Уведомление о заявке в друзья
def notify_friend_request(receiver_id):
    user = db.session.get(User, int(get_jwt_identity()))

    message = f"Пользователь {user.name} отправил вам заявку в друзья."
    create_notification(
        receiver_id=receiver_id,
        message=message,
        type='invitation',
        sender_id=int(get_jwt_identity())
    )

def notify_friend_request_response(friend_request, accepted):
    sender = db.session.get(User, friend_request.sender_id)
    receiver = db.session.get(User, friend_request.receiver_id)
    
    if accepted:
        message = f"Пользователь {receiver.name} принял вашу заявку в друзья."
    else:
        message = f"Пользователь {receiver.name} отклонил вашу заявку в друзья."
    
    create_notification(
        receiver_id=friend_request.sender_id,
        message=message,
        type='result',
        sender_id=friend_request.receiver_id
    )

# 2. Уведомление о приглашении в группу
def notify_group_invitation(receiver_id, group_id):
    group = db.session.get(Group, group_id)
    message = f"Вас пригласили в группу '{group.name}'."
    create_notification(
        receiver_id=receiver_id,
        message=message,
        type='invitation',
        group_id=group_id
    )

def notify_group_invitation_response(user_id, group_id, accepted=True):
    group = db.session.get(Group, group_id)
    user = db.session.get(User, user_id)
    
    if accepted:
        message = f"Пользователь {user.name} принял приглашение в группу '{group.name}'."
    else:
        message = f"Пользователь {user.name} отклонил приглашение в группу '{group.name}'."
    
    # Отправляем уведомление создателю группы
    create_notification(
        receiver_id=group.created_by,
        message=message,
        type='result',
        sender_id=user_id,
        group_id=group_id
    )

# 3. Уведомление о добавлении в событие
def notify_added_to_event(event_id, user_id):
    event = db.session.get(Event, event_id)
    message = f"Вас добавили в событие '{event.title}' на {event.date_time.strftime('%d.%m.%Y %H:%M')}."
    create_notification(
        receiver_id=user_id,
        message=message,
        type='result',
        sender_id=int(get_jwt_identity()),
        event_id=event_id,
        group_id=event.group_id
    )

# 4. Уведомление о создании черновика события
def notify_event_draft_created(event_draft_id):
    event_draft = db.session.get(EventDraft, event_draft_id)
    group = db.session.get(Group, event_draft.group_id)
    
    # Получаем всех участников группы
    members = GroupMember.query.filter_by(group_id=group.id).all()
    
    message = f"В группе '{group.name}' создан новый черновик события '{event_draft.title}'. Пожалуйста, укажите вашу доступность."
    
    for member in members:
        if member.user_id != int(get_jwt_identity()):  # Не уведомляем создателя
            create_notification(
                receiver_id=member.user_id,
                message=message,
                type='invitation',
                group_id=group.id,
                event_draft_id=event_draft_id
            )

# 5. Уведомление о том, что черновик стал событием
def notify_event_draft_success(event_draft_id):
    event_draft = db.session.get(EventDraft, event_draft_id)
    group = db.session.get(Group, event_draft.group_id)
    event = Event.query.filter_by(event_draft_id=event_draft_id).first()
    
    if not event:
        return
    
    # Получаем всех участников события
    participants = EventParticipant.query.filter_by(event_id=event.id).all()
    
    message = (f"Черновик события '{event_draft.title}' в группе '{group.name}' был успешно согласован. "
               f"Событие запланировано на {event.date_time.strftime('%d.%m.%Y %H:%M')}.")
    
    for participant in participants:
        create_notification(
            receiver_id=participant.user_id,
            message=message,
            type='result',
            event_id=event.id,
            group_id=group.id
        )

# 6. Уведомление о том, что черновик не смог стать событием
def notify_event_draft_failed(event_draft_id, reason=""):
    event_draft = db.session.get(EventDraft, event_draft_id)
    group = db.session.get(Group, event_draft.group_id)
    
    # Получаем всех участников группы
    members = GroupMember.query.filter_by(group_id=group.id).all()
    
    message = (f"Черновик события '{event_draft.title}' в группе '{group.name}' не был согласован. "
               f"{reason}")
    
    for member in members:
        create_notification(
            receiver_id=member.user_id,
            message=message,
            type='result',
            group_id=group.id,
            event_draft_id=event_draft_id
        )

# 7. Уведомление об изменении и удалении события
def notify_event_participants(event, message, type):
    participants = EventParticipant.query.filter_by(event_id=event.id).all()
    for p in participants:
        if p.user_id != int(get_jwt_identity()):
            create_notification(
                receiver_id=p.user_id,
                message=message,
                type=type,
                event_id=event.id,
                group_id=event.group_id,
                event_draft_id=event.event_draft_id
            )

#----------------GET_методы---------------------------

class UserNotifications(Resource):
    @jwt_required()
    def get(self):
        notifications = Notification.query.filter_by(receiver_id=int(get_jwt_identity())).order_by(Notification.created_at.desc()).all()
        
        return [{
            "id": n.id,
            "sender_id": n.sender_id,
            "sender_name": db.session.get(User, n.sender_id).name if n.sender_id else "Система",
            "message": n.message,
            "type": n.type,
            "read_status": n.read_status,
            "created_at": n.created_at.isoformat(),
            "event_id": n.event_id,
            "group_id": n.group_id,
            "event_draft_id": n.event_draft_id
        } for n in notifications]

class UserInvitationNotifications(Resource):
    @jwt_required()
    def get(self):
        notifications = Notification.query.filter(
            Notification.receiver_id == int(get_jwt_identity()),
            Notification.type == 'invitation'
        ).order_by(Notification.created_at.desc()).all()
        
        return [{
            "id": n.id,
            "sender_id": n.sender_id,
            "sender_name": db.session.get(User, n.sender_id).name if n.sender_id else "Система",
            "message": n.message,
            "type": n.type,
            "read_status": n.read_status,
            "created_at": n.created_at.isoformat(),
            "group_id": n.group_id  # Для заявок в друзья group_id будет null
        } for n in notifications]

class UserGeneralNotifications(Resource):
    @jwt_required()
    def get(self):
        notifications = Notification.query.filter(
            Notification.receiver_id == int(get_jwt_identity()),
            Notification.type != 'invitation'
        ).order_by(Notification.created_at.desc()).all()
        
        return [{
            "id": n.id,
            "sender_id": n.sender_id,
            "sender_name": db.session.get(User, n.sender_id).name if n.sender_id else "Система",
            "message": n.message,
            "type": n.type,
            "read_status": n.read_status,
            "created_at": n.created_at.isoformat(),
            "event_id": n.event_id,
            "group_id": n.group_id,
            "event_draft_id": n.event_draft_id
        } for n in notifications]

#---------------POST_метод---------------------------------------
class MarkNotificationAsRead(Resource):
    @jwt_required()
    def post(self, notification_id):
        # Получаем уведомление с проверкой владельца
        notification = Notification.query.filter(
            Notification.id == notification_id,
            Notification.receiver_id == int(get_jwt_identity())
        ).first()

        if not notification:
            return {"error": "Уведомление не найдено"}, 404

        # Если это не заявка (invitation) - удаляем
        if notification.type != 'invitation':
            db.session.delete(notification)
            action = "Уведомление удалено"
        else:
            # Для заявок просто помечаем прочитанным
            notification.read_status = True
            action = "Уведомление помечено как прочитанное"

        db.session.commit()
        
        return {
            "message": action,
            "deleted": notification.type != 'invitation'
        }