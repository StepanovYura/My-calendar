from models.models import Notification, EventParticipant, User, Group, GroupMember, Event, EventDraft, EventConsent
from api.notifications import notify_event_participants, notify_group_invitation
from flask_login import current_user, login_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from flask_restful import Resource
from flask import request
from extensions import db
import os

#  Создание группы (POST /groups)
class GroupCreate(Resource):
    @jwt_required()
    def post(self):
        data = request.form
        avatar = request.files.get('avatar')
        host_url = request.host_url.rstrip('/')  # ВОЗМОЖНО БУДЕТ ВСЁ ЛОМАТЬ И СТОИТ БЕЗ НЕГО

        if not data.get('name'):
            return {"error": "Название группы обязательно"}, 400

        new_group = Group(
            name=data['name'],
            description=data.get('description', ''),
            created_by=int(get_jwt_identity()),
            avatar_url=data.get('avatar_url')
        )
        db.session.add(new_group)
        db.session.commit()

        if avatar:
            filename = f"group_{new_group.id}_{avatar.filename}"
            filepath = os.path.join("static", "avatars", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            avatar.save(filepath)
            new_group.avatar_url = f"{host_url}/static/avatars/{filename}"

        # Автоматически добавляем создателя в участники
        membership = GroupMember(
            group_id=new_group.id,
            user_id=int(get_jwt_identity())
        )
        db.session.add(membership)
        db.session.commit()

        return {
            "message": "Группа создана",
            "group_id": new_group.id
        }, 201

# Вступление в группу (POST /groups/<int:group_id>/join)
class GroupJoin(Resource):
    @jwt_required()
    def post(self, group_id):
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Группа не найдена"}, 404

        # Проверяем, не состоит ли уже пользователь в группе
        existing_member = GroupMember.query.filter_by(
            group_id=group_id,
            user_id=int(get_jwt_identity())
        ).first()
        
        if existing_member:
            return {"error": "Вы уже состоите в этой группе"}, 400

        membership = GroupMember(
            group_id=group_id,
            user_id=int(get_jwt_identity())
        )
        db.session.add(membership)
        db.session.commit()

        return {"message": "Вы успешно вступили в группу"}

# Выход из группы (POST /groups/<int:group_id>/leave)
class GroupLeave(Resource):
    @jwt_required()
    def post(self, group_id):
        membership = GroupMember.query.filter_by(
            group_id=group_id,
            user_id=int(get_jwt_identity())
        ).first()

        if not membership:
            return {"error": "Вы не состоите в этой группе"}, 400

        group = db.session.get(Group, group_id)
        
        # Создатель не может покинуть группу (должен сначала удалить её или передать права)
        if group.created_by == int(get_jwt_identity()):
            return {"error": "Создатель не может покинуть группу"}, 403

        db.session.delete(membership)
        db.session.commit()

        return {"message": "Вы вышли из группы"}

# Удаление группы (DELETE /groups/<int:group_id>)
class GroupDelete(Resource):
    @jwt_required()
    def delete(self, group_id):
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Группа не найдена"}, 404

        if group.created_by != int(get_jwt_identity()):
            return {"error": "Только создатель может удалить группу"}, 403

        db.session.delete(group)
        db.session.commit()

        return {"message": "Группа удалена"}

# Редактирование группы (PUT /groups/<int:group_id>)
class GroupEdit(Resource):
    @jwt_required()
    def put(self, group_id):
        group = db.session.get(Group, group_id)
        host_url = request.host_url.rstrip('/') # ВОЗМОЖНО БУДЕТ ВСЁ ЛОМАТЬ И СТОИТ БЕЗ НЕГО
        if not group:
            return {"error": "Группа не найдена"}, 404

        if group.created_by != int(get_jwt_identity()):
            return {"error": "Только создатель может редактировать группу"}, 403

        data = request.form
        avatar = request.files.get('avatar')
        if not data:
            return {"error": "Нет данных для обновления"}, 400

        group.name = data.get('name', group.name)
        group.description = data.get('description', group.description)
        if avatar:
            filename = f"group_{group.id}_{avatar.filename}"
            filepath = os.path.join("static", "avatars", filename)
            avatar.save(filepath)
            group.avatar_url = f"{host_url}/static/avatars/{filename}"

        db.session.commit()

        return {"message": "Информация о группе обновлена"}

# Приглашение в группу (POST /groups/<int:group_id>/invite)
class GroupInvite(Resource):
    @jwt_required()
    def post(self, group_id):
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return {"error": "Не указан пользователь"}, 400

        # Проверяем, что группа существует и текущий пользователь является участником
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Группа не найдена"}, 404

        is_member = GroupMember.query.filter_by(
            group_id=group_id,
            user_id=int(get_jwt_identity())
        ).first()
        
        if not is_member:
            return {"error": "Вы не состоите в этой группе"}, 403

        # Проверяем, что приглашаемый пользователь существует
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "Пользователь не найден"}, 404

        # Проверяем, не состоит ли уже пользователь в группе
        existing_member = GroupMember.query.filter_by(
            group_id=group_id,
            user_id=user_id
        ).first()
        
        if existing_member:
            return {"error": "Пользователь уже в группе"}, 400

        # Отправляем уведомление (используем функцию из notification.py)
        notify_group_invitation(user_id, group_id)

        return {"message": "Приглашение отправлено"}

# Получение списка групп пользователя (GET /groups/my)
class UserGroups(Resource):
    @jwt_required()
    def get(self):
        groups = Group.query.join(GroupMember).filter(
            GroupMember.user_id == int(get_jwt_identity())
        ).all()

        return [{
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "created_by": g.created_by,
            "avatar_url": g.avatar_url,
            "is_creator": g.created_by == int(get_jwt_identity())
        } for g in groups]

# Получение информации о конкретной группе (GET /groups/<int:group_id>)    
class GroupDetail(Resource):
    @jwt_required()
    def get(self, group_id):
        group = db.session.get(Group, group_id)
        user = db.session.get(User, int(get_jwt_identity()))
        creator = db.session.get(User, group.created_by)
        members = GroupMember.query.filter_by(group_id=group_id).all()
        member_users = User.query.filter(User.id.in_([m.user_id for m in members])).all()
        user_map = {user.id: user.name for user in member_users}

        if not group:
            return {"error": "Группа не найдена"}, 404

        # Проверяем, что пользователь состоит в группе
        is_member = GroupMember.query.filter_by(
            group_id=group_id,
            user_id=int(get_jwt_identity())
        ).first()
        
        if not is_member and user.role != 'admin':
            return {"error": "Вы не состоите в этой группе"}, 403

        # Активные черновики (голосования)
        active_drafts = EventDraft.query.filter_by(
            group_id=group_id,
            status='voting'
        ).all()

        drafts_data = []
        for d in active_drafts:
            # Получаем голоса по данному черновику
            consents = EventConsent.query.filter_by(event_draft_id=d.id).all()
            drafts_data.append({
                "id": d.id,
                "title": d.title,
                "status": d.status,
                "created_at": d.created_at.isoformat(),
                "created_by": d.created_by,
                "date_time": d.created_at.isoformat(),  # если нет отдельного поля даты события
                "consents": [
                    {
                        "user_id": c.user_id,
                        "consent": c.consent
                    }
                    for c in consents
                ]
            })



        return {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "created_by": group.created_by,
            "creator_name": creator.name if creator else "Неизвестно",
            "avatar_url": group.avatar_url,
            "is_creator": group.created_by == int(get_jwt_identity()),
            "members": [{
                "user_id": m.user_id,
                "user_name": user_map.get(m.user_id, "—"),
                "joined_at": m.joined_at.isoformat()
            } for m in members],
            "drafts": drafts_data #if len(drafts_data) != 0 else "Активных голосований нет"
        }

class GroupSchedule(Resource):
    @jwt_required()
    def get(self, group_id):
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Группа не найдена"}, 404

        is_member = GroupMember.query.filter_by(
            group_id=group_id,
            user_id=int(get_jwt_identity())
        ).first()

        user = db.session.get(User, int(get_jwt_identity()))

        if not is_member and user.role != 'admin':
            return {"error": "Вы не состоите в этой группе"}, 403

        events = Event.query.filter_by(group_id=group_id).all()

        return [{
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "date_time": e.date_time.isoformat(),
            "duration_minutes": e.duration_minutes
        } for e in events]

class GroupMembers(Resource):
    @jwt_required()
    def get(self, group_id):
        group = db.session.get(Group, group_id)
        members = GroupMember.query.filter_by(group_id=group_id).all()
        member_users = User.query.filter(User.id.in_([m.user_id for m in members])).all()
        user_map = {user.id: user.name for user in member_users}
        if not group:
            return {'error': 'Группа не найдена'}, 404

        return {"members": [{
                "user_id": m.user_id,
                "user_name": user_map.get(m.user_id, "—"),
            } for m in members]}
    
class GroupInviteResponse(Resource):
    @jwt_required()
    def post(self, group_id):
        data = request.get_json()
        action = data.get('action')

        if action not in ['accept', 'decline']:
            return {"error": "Некорректное действие"}, 400

        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Группа не найдена"}, 404

        user_id = int(get_jwt_identity())

        if action == 'accept':
            # Проверяем, не состоит ли уже
            existing_member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
            if existing_member:
                return {"error": "Вы уже в группе"}, 400

            membership = GroupMember(group_id=group_id, user_id=user_id)
            db.session.add(membership)
            db.session.commit()

            # Уведомляем создателя
            from api.notifications import notify_group_invitation_response
            notify_group_invitation_response(user_id, group_id, accepted=True)

            return {"message": "Вы приняли приглашение"}

        else:
            from api.notifications import notify_group_invitation_response
            notify_group_invitation_response(user_id, group_id, accepted=False)
            return {"message": "Вы отклонили приглашение"}
