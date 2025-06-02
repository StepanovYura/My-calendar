from models.models import Notification, EventParticipant, User, Group, GroupMember, Event, EventDraft
from api.notifications import notify_event_participants, notify_group_invitation
from flask_login import current_user, login_required
from datetime import datetime, date
from flask_restful import Resource
from flask import request
from extensions import db

#  Создание группы (POST /groups)
class GroupCreate(Resource):
    @login_required
    def post(self):
        data = request.get_json()
        if not data.get('name'):
            return {"error": "Название группы обязательно"}, 400

        new_group = Group(
            name=data['name'],
            description=data.get('description', ''),
            created_by=current_user.id,
            avatar_url=data.get('avatar_url')
        )
        db.session.add(new_group)
        db.session.commit()

        # Автоматически добавляем создателя в участники
        membership = GroupMember(
            group_id=new_group.id,
            user_id=current_user.id
        )
        db.session.add(membership)
        db.session.commit()

        return {
            "message": "Группа создана",
            "group_id": new_group.id
        }, 201

# Вступление в группу (POST /groups/<int:group_id>/join)
class GroupJoin(Resource):
    @login_required
    def post(self, group_id):
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Группа не найдена"}, 404

        # Проверяем, не состоит ли уже пользователь в группе
        existing_member = GroupMember.query.filter_by(
            group_id=group_id,
            user_id=current_user.id
        ).first()
        
        if existing_member:
            return {"error": "Вы уже состоите в этой группе"}, 400

        membership = GroupMember(
            group_id=group_id,
            user_id=current_user.id
        )
        db.session.add(membership)
        db.session.commit()

        return {"message": "Вы успешно вступили в группу"}

# Выход из группы (POST /groups/<int:group_id>/leave)
class GroupLeave(Resource):
    @login_required
    def post(self, group_id):
        membership = GroupMember.query.filter_by(
            group_id=group_id,
            user_id=current_user.id
        ).first()

        if not membership:
            return {"error": "Вы не состоите в этой группе"}, 400

        group = db.session.get(Group, group_id)
        
        # Создатель не может покинуть группу (должен сначала удалить её или передать права)
        if group.created_by == current_user.id:
            return {"error": "Создатель не может покинуть группу"}, 403

        db.session.delete(membership)
        db.session.commit()

        return {"message": "Вы вышли из группы"}

# Удаление группы (DELETE /groups/<int:group_id>)
class GroupDelete(Resource):
    @login_required
    def delete(self, group_id):
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Группа не найдена"}, 404

        if group.created_by != current_user.id:
            return {"error": "Только создатель может удалить группу"}, 403

        db.session.delete(group)
        db.session.commit()

        return {"message": "Группа удалена"}

# Редактирование группы (PUT /groups/<int:group_id>)
class GroupEdit(Resource):
    @login_required
    def put(self, group_id):
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Группа не найдена"}, 404

        if group.created_by != current_user.id:
            return {"error": "Только создатель может редактировать группу"}, 403

        data = request.get_json()
        if not data:
            return {"error": "Нет данных для обновления"}, 400

        group.name = data.get('name', group.name)
        group.description = data.get('description', group.description)
        group.avatar_url = data.get('avatar_url', group.avatar_url)

        db.session.commit()

        return {"message": "Информация о группе обновлена"}

# Приглашение в группу (POST /groups/<int:group_id>/invite)
class GroupInvite(Resource):
    @login_required
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
            user_id=current_user.id
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
    @login_required
    def get(self):
        groups = Group.query.join(GroupMember).filter(
            GroupMember.user_id == current_user.id
        ).all()

        return [{
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "created_by": g.created_by,
            "avatar_url": g.avatar_url,
            "is_creator": g.created_by == current_user.id
        } for g in groups]

# Получение информации о конкретной группе (GET /groups/<int:group_id>)    
class GroupDetail(Resource):
    @login_required
    def get(self, group_id):
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Группа не найдена"}, 404

        # Проверяем, что пользователь состоит в группе
        is_member = GroupMember.query.filter_by(
            group_id=group_id,
            user_id=current_user.id
        ).first()
        
        if not is_member and current_user.role != 'admin':
            return {"error": "Вы не состоите в этой группе"}, 403

        members = GroupMember.query.filter_by(group_id=group_id).all()

        return {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "created_by": group.created_by,
            "avatar_url": group.avatar_url,
            "is_creator": group.created_by == current_user.id,
            "members": [{
                "user_id": m.user_id,
                "joined_at": m.joined_at.isoformat()
            } for m in members]
        }