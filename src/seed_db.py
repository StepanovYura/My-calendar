from extensions import db
from models.models import (
    User, Friend, Group, GroupMember, 
    EventDraft, AvailabilitySlot, EventConsent,
    Event, EventParticipant, Notification
)
from datetime import datetime, timedelta
import random

# Очистка всех таблиц (осторожно, удалит все данные!)
def clear_tables():
    print("Clearing existing data...")
    db.session.query(Notification).delete()
    db.session.query(EventParticipant).delete()
    db.session.query(Event).delete()
    db.session.query(EventConsent).delete()
    db.session.query(AvailabilitySlot).delete()
    db.session.query(EventDraft).delete()
    db.session.query(GroupMember).delete()
    db.session.query(Group).delete()
    db.session.query(Friend).delete()
    db.session.query(User).delete()
    db.session.commit()

# Создание тестовых пользователей
def create_users():
    print("Creating users...")
    users = [
        User(
            name="Алексей Петров",
            email="alex@example.com",
            password_hash="hashed_password_123",  # В реальном приложении используйте хеширование!
            role="admin",
            privacy_setting="all"
        ),
        User(
            name="Мария Иванова",
            email="maria@example.com",
            password_hash="hashed_password_456",
            role="user",
            privacy_setting="all"
        ),
        User(
            name="Иван Сидоров",
            email="ivan@example.com",
            password_hash="hashed_password_789",
            role="user",
            privacy_setting="none"
        )
    ]
    db.session.add_all(users)
    db.session.commit()
    return users

# Создание дружеских связей
def create_friends(users):
    print("Creating friends...")
    friend_requests = [
        Friend(sender_id=users[0].id, receiver_id=users[1].id, status="accepted"),
        Friend(sender_id=users[1].id, receiver_id=users[2].id, status="pending"),
    ]
    db.session.add_all(friend_requests)
    db.session.commit()

# Создание групп
def create_groups(users):
    print("Creating groups...")
    groups = [
        Group(
            name="Команда разработки",
            description="Основная команда backend-разработчиков",
            created_by=users[0].id,
        ),
        Group(
            name="Дизайнеры",
            description="Команда UI/UX дизайнеров",
            created_by=users[1].id,
        )
    ]
    db.session.add_all(groups)
    db.session.commit()
    return groups

# Добавление участников в группы
def create_group_members(users, groups):
    print("Adding group members...")
    memberships = [
        GroupMember(group_id=groups[0].id, user_id=users[0].id),
        GroupMember(group_id=groups[0].id, user_id=users[1].id),
        GroupMember(group_id=groups[1].id, user_id=users[1].id),
        GroupMember(group_id=groups[1].id, user_id=users[2].id),
    ]
    db.session.add_all(memberships)
    db.session.commit()

# Создание черновиков событий
def create_event_drafts(users, groups):
    print("Creating event drafts...")
    drafts = [
        EventDraft(
            group_id=groups[0].id,
            title="Планирование спринта",
            description="Обсудим задачи на следующий спринт",
            created_by=users[0].id,
            status="voting",
            event_type="meeting",
            color="#4287f5"
        ),
        EventDraft(
            group_id=groups[1].id,
            title="Обзор дизайна",
            description="Презентация новых макетов",
            created_by=users[1].id,
            status="voting",
            event_type="presentation",
            color="#f54242"
        )
    ]
    db.session.add_all(drafts)
    db.session.commit()
    return drafts

# Создание слотов доступности
def create_availability_slots(users, drafts):
    print("Creating availability slots...")
    slots = []
    for draft in drafts:
        for user in users:
            start_time = datetime.now() + timedelta(days=random.randint(1, 3), hours=random.randint(9, 18))
            end_time = start_time + timedelta(hours=1)
            slots.append(
                AvailabilitySlot(
                    event_draft_id=draft.id,
                    user_id=user.id,
                    start_time=start_time,
                    end_time=end_time
                )
            )
    db.session.add_all(slots)
    db.session.commit()

# Создание подтверждений участия
def create_event_consents(users, drafts):
    print("Creating event consents...")
    consents = []
    for draft in drafts:
        for user in users:
            consents.append(
                EventConsent(
                    event_draft_id=draft.id,
                    user_id=user.id,
                    consent=random.choice([True, False])
                )
            )
    db.session.add_all(consents)
    db.session.commit()

# Создание событий
def create_events(users, groups, drafts):
    print("Creating events...")
    events = [
        Event(
            group_id=groups[0].id,
            event_draft_id=drafts[0].id,
            title="Спринт #5",
            description="Финальное обсуждение задач",
            date_time=datetime.now() + timedelta(days=2, hours=12),
            duration_minutes=90,
            created_by=users[0].id,
            event_type="meeting",
            color="#4287f5",
            status="active"
        ),
        Event(
            group_id=groups[1].id,
            event_draft_id=drafts[1].id,
            title="Презентация дизайна",
            description="Обсуждаем новый UI",
            date_time=datetime.now() + timedelta(days=3, hours=15),
            duration_minutes=60,
            created_by=users[1].id,
            event_type="presentation",
            color="#f54242",
            status="active"
        )
    ]
    db.session.add_all(events)
    db.session.commit()
    return events

# Добавление участников событий
def create_event_participants(users, events):
    print("Adding event participants...")
    participants = []
    for event in events:
        for user in users:
            if random.choice([True, False]):  # 50% chance of participation
                participants.append(
                    EventParticipant(
                        event_id=event.id,
                        user_id=user.id
                    )
                )
    db.session.add_all(participants)
    db.session.commit()

# Создание уведомлений
def create_notifications(users, events):
    print("Creating notifications...")
    notifications = [
        Notification(
            receiver_id=users[1].id,
            sender_id=users[0].id,
            message="Вас добавили в событие 'Спринт #5'",
            type="invitation",
            event_id=events[0].id
        ),
        Notification(
            receiver_id=users[2].id,
            sender_id=users[1].id,
            message="Пожалуйста, подтвердите участие в 'Презентация дизайна'",
            type="reminder",
            event_id=events[1].id
        )
    ]
    db.session.add_all(notifications)
    db.session.commit()

# Основная функция
def seed_database():
    print("Starting database seeding...")
    clear_tables()
    users = create_users()
    create_friends(users)
    groups = create_groups(users)
    create_group_members(users, groups)
    drafts = create_event_drafts(users, groups)
    create_availability_slots(users, drafts)
    create_event_consents(users, drafts)
    events = create_events(users, groups, drafts)
    create_event_participants(users, events)
    create_notifications(users, events)
    print("Database seeded successfully!")

if __name__ == "__main__":
    from app import app  # Импортируйте ваш Flask app
    with app.app_context():
        seed_database()