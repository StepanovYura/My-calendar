from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime
from extensions import db

# ENUM-типы
privacy_setting = ENUM('all', 'none', name='privacy_setting', schema='public', create_type=False)
user_role = ENUM('user', 'admin', name='user_role', schema='public', create_type=False)
friend_status = ENUM('pending', 'accepted', 'declined', name='friend_status', schema='public', create_type=False)
draft_status = ENUM('voting', 'successful', 'failed', name='draft_status', schema='public', create_type=False)
event_status = ENUM('active', 'cancelled', name='event_status', schema='public', create_type=False)
notification_type = ENUM('invitation', 'reminder', 'update', 'result', schema='public', name='notification_type', create_type=False)

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    privacy_setting = db.Column(privacy_setting, default='all')
    role = db.Column(user_role, default='user')
    avatar_url = db.Column(db.Text)

    # связи
    created_groups = db.relationship('Group', backref='creator', foreign_keys='Group.created_by')
    created_drafts = db.relationship('EventDraft', backref='creator', foreign_keys='EventDraft.created_by')
    created_events = db.relationship('Event', backref='creator', foreign_keys='Event.created_by')

    sent_friend_requests = db.relationship('Friend', foreign_keys='Friend.sender_id', backref='sender', cascade='all, delete-orphan')
    received_friend_requests = db.relationship('Friend', foreign_keys='Friend.receiver_id', backref='receiver', cascade='all, delete-orphan')

    group_memberships = db.relationship('GroupMember', backref='user', cascade='all, delete-orphan')
    event_participation = db.relationship('EventParticipant', backref='user', cascade='all, delete-orphan')
    availability_slots = db.relationship('AvailabilitySlot', backref='user', cascade='all, delete-orphan')
    consents = db.relationship('EventConsent', backref='user', cascade='all, delete-orphan')

    sent_notifications = db.relationship('Notification', foreign_keys='Notification.sender_id', backref='sender', passive_deletes=True)
    received_notifications = db.relationship('Notification', foreign_keys='Notification.receiver_id', backref='receiver', cascade='all, delete-orphan')


class Friend(db.Model):
    __tablename__ = 'friends'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(friend_status, nullable=False)


class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    avatar_url = db.Column(db.Text)

    members = db.relationship('GroupMember', backref='group', cascade='all, delete-orphan')
    drafts = db.relationship('EventDraft', backref='group', cascade='all, delete-orphan')
    events = db.relationship('Event', backref='group', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='group', cascade='all, delete-orphan')


class GroupMember(db.Model):
    __tablename__ = 'groupmember'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


class EventDraft(db.Model):
    __tablename__ = 'eventdraft'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    status = db.Column(draft_status, default='voting')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    event_type = db.Column(db.String(100))
    color = db.Column(db.String(7))
    date = db.Column(db.Date, nullable=False)
    
    slots = db.relationship('AvailabilitySlot', backref='event_draft', cascade='all, delete-orphan')
    consents = db.relationship('EventConsent', backref='event_draft', cascade='all, delete-orphan')
    events = db.relationship('Event', backref='event_draft', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='event_draft', cascade='all, delete-orphan')


class AvailabilitySlot(db.Model):
    __tablename__ = 'availabilityslot'

    id = db.Column(db.Integer, primary_key=True)
    event_draft_id = db.Column(db.Integer, db.ForeignKey('eventdraft.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)


class EventConsent(db.Model):
    __tablename__ = 'eventconsent'

    id = db.Column(db.Integer, primary_key=True)
    event_draft_id = db.Column(db.Integer, db.ForeignKey('eventdraft.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    consent = db.Column(db.Boolean, nullable=False)
    responded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id', ondelete='CASCADE'), nullable=True)
    event_draft_id = db.Column(db.Integer, db.ForeignKey('eventdraft.id', ondelete='SET NULL'))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    date_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    event_type = db.Column(db.String(100))
    color = db.Column(db.String(7))
    status = db.Column(event_status, default='active')

    participants = db.relationship('EventParticipant', backref='event', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='event', cascade='all, delete-orphan')


class EventParticipant(db.Model):
    __tablename__ = 'eventparticipant'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)


class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    message = db.Column(db.Text, nullable=False)
    type = db.Column(notification_type)
    read_status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id', ondelete='SET NULL'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id', ondelete='SET NULL'))
    event_draft_id = db.Column(db.Integer, db.ForeignKey('eventdraft.id', ondelete='SET NULL'))
