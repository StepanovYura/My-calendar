from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from extensions import db
from models.models import EventDraft, GroupMember, EventConsent, AvailabilitySlot, Event, EventParticipant
from api.notifications import notify_event_draft_created, notify_event_draft_failed, notify_event_draft_success

class EventDraftCreate(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        
        # Проверка обязательных полей
        required_fields = ['title', 'group_id', 'date']
        if not all(field in data for field in required_fields):
            return {"error": "Необходимы title, group_id и date"}, 400
        
        # Проверка членства в группе
        membership = GroupMember.query.filter_by(
            group_id=data['group_id'],
            user_id=int(get_jwt_identity())
        ).first()
        if not membership:
            return {"error": "Вы не состоите в этой группе"}, 403
        
        # Создание черновика
        new_draft = EventDraft(
            title=data['title'],
            description=data.get('description', ''),
            group_id=data['group_id'],
            created_by=int(get_jwt_identity()),
            date=data['date'],
            status='voting'
        )
        db.session.add(new_draft)
        db.session.commit()
        
        # Проверка формата слотов
        if 'slots' in data:
            for slot in data['slots']:
                if 'start' not in slot or 'end' not in slot:
                    return {"error": "Каждый слот должен содержать start и end"}, 400

        # Обработка слотов (если переданы)
        slots = data.get('slots')
        if slots:
            for slot in slots:
                db.session.add(AvailabilitySlot(
                    event_draft_id=new_draft.id,
                    user_id=int(get_jwt_identity()),
                    start_time=datetime.fromisoformat(slot['start']),
                    end_time=datetime.fromisoformat(slot['end'])
                ))

        # Автоматическое согласие создателя
        db.session.add(EventConsent(
            event_draft_id=new_draft.id,
            user_id=int(get_jwt_identity()),
            consent=True
        ))
        
        db.session.commit()
        
        # Уведомление участников
        notify_event_draft_created(new_draft.id)
        
        return {
            "message": "Черновик создан",
            "draft_id": new_draft.id,
        }, 201

class VoteForDraft(Resource):
    @jwt_required()
    def post(self, event_draft_id):
        data = request.get_json()
        
        # Проверка голоса
        if 'consent' not in data or not isinstance(data['consent'], bool):
            return {"error": "Необходимо указать consent (true/false)"}, 400
        
        # Получаем черновик
        draft = db.session.get(EventDraft, event_draft_id)
        if not draft:
            return {"error": "Черновик не найден"}, 404
        
        consent = EventConsent.query.filter_by(
            event_draft_id=event_draft_id,
            user_id=int(get_jwt_identity())
        ).first()
        
        if not consent:
            # Проверяем, что пользователь действительно участник группы
            if not GroupMember.query.filter_by(
                group_id=draft.group_id,
                user_id=int(get_jwt_identity())
            ).first():
                return {"error": "Вы не участник группы"}, 403
                
            consent = EventConsent(
                event_draft_id=event_draft_id,
                user_id=int(get_jwt_identity()),
                consent=data['consent']
            )
            db.session.add(consent)
        else:
            if consent.consent is not None:  # Уже голосовал
                return {"error": "Вы уже проголосовали"}, 400
            consent.consent = data['consent']
        
        db.session.commit()
        
        # "за" и временные слоты должны отправляться в одном запросе вроде!!!!
        # Если голос "за" и есть слоты - сохраняем их
        if data['consent'] and data.get('slots'):
            # пока что пользователь может проголосовать единожды в черновике!!!
            # Удаляем старые слоты
            AvailabilitySlot.query.filter_by(
                event_draft_id=event_draft_id,
                user_id=int(get_jwt_identity())
            ).delete()
            
            # Добавляем новые
            for slot in data['slots']:
                db.session.add(AvailabilitySlot(
                    event_draft_id=event_draft_id,
                    user_id=int(get_jwt_identity()),
                    start_time=datetime.fromisoformat(slot['start']),
                    end_time=datetime.fromisoformat(slot['end'])
                ))
            db.session.commit()

        # После сохранения голоса проверим — все ли проголосовали
        total_members = GroupMember.query.filter_by(group_id=draft.group_id).count()
        votes = EventConsent.query.filter_by(event_draft_id=event_draft_id).count()

        if votes >= total_members:
            # все участники проголосовали, запускаем финализацию
            finalize = FinalizeDraft()
            return finalize.post(event_draft_id)
        
        return {"message": "Ваш голос учтен"}

class FinalizeDraft(Resource):
    @jwt_required()
    def post(self, event_draft_id):
        draft = db.session.get(EventDraft, event_draft_id)
        if not draft:
            return {"error": "Черновик не найден"}, 404
        
        # Проверка что все участники проголосовали
        total_members = GroupMember.query.filter_by(group_id=draft.group_id).count()
        votes = EventConsent.query.filter_by(event_draft_id=event_draft_id).count()
        
        if votes < total_members:
            return {"error": "Не все участники проголосовали"}, 400
        
        # Подсчет голосов
        agreed_votes = EventConsent.query.filter_by(
            event_draft_id=event_draft_id,
            consent=True
        ).all()      
        
        # Поиск общего временного слота
        common_slot = self.find_common_slot(event_draft_id, agreed_votes)
        
        if not common_slot:
            draft.status = 'failed'
            db.session.commit()
            notify_event_draft_failed(event_draft_id, "Не найдено подходящего времени для всех участников")
            return {"message": "Не найдено общего временного слота", "status": "failed"}
        
        date_time = datetime.combine(
            draft.date,
            common_slot['start'].time()
        )   
        # Создание события
        event = Event(
            title=draft.title,
            description=draft.description,
            group_id=draft.group_id,
            event_draft_id=draft.id,
            date_time=date_time,
            duration_minutes=int((common_slot['end'] - common_slot['start']).total_seconds() / 60),
            created_by=draft.created_by
        )
        db.session.add(event)
        db.session.flush()
        # Добавление участников
        for vote in agreed_votes:
            db.session.add(EventParticipant(
                event_id=event.id,
                user_id=vote.user_id
            ))
        
        draft.status = 'successful'
        db.session.commit()
        
        # Оповещение участников
        notify_event_draft_success(event_draft_id)
        
        return {
            "message": "Событие создано",
            "event_id": event.id,
            "start_time": common_slot['start'].isoformat(),
            "end_time": common_slot['end'].isoformat()
        }

    def find_common_slot(self, event_draft_id, agreed_votes):
        """Поиск общего временного интервала среди всех участников"""
        # Получаем слоты всех согласившихся участников
        all_slots = []
        for vote in agreed_votes:
            user_slots = AvailabilitySlot.query.filter_by(
                event_draft_id=event_draft_id,
                user_id=vote.user_id
            ).order_by(AvailabilitySlot.start_time).all()
                
            all_slots.append(user_slots)
        
        # Находим пересечения всех слотов
        common_slots = []
        for base_slot in all_slots[0]:
            current_start = base_slot.start_time
            current_end = base_slot.end_time
            
            for other_user_slots in all_slots[1:]:
                found = False
                for slot in other_user_slots:
                    overlap_start = max(current_start, slot.start_time)
                    overlap_end = min(current_end, slot.end_time)
                    
                    if overlap_start < overlap_end:  # Есть пересечение
                        current_start = overlap_start
                        current_end = overlap_end
                        found = True
                        break
                
                if not found:
                    current_start = None
                    break
            
            if current_start and (current_end - current_start) >= timedelta(hours=1):
                common_slots.append({
                    'start': current_start,
                    'end': current_end,
                    'duration': (current_end - current_start).total_seconds() # почему секунды? может минуты?
                })
        
        if not common_slots:
            return None
        
        # Выбираем самый длинный слот, а при равенстве - самый ранний
        common_slots.sort(key=lambda x: (-x['duration'], x['start']))
        return common_slots[0]