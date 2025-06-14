from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from calendar import monthrange
from models.models import db, Event, User, EventParticipant

class MatchDays(Resource):
    @jwt_required()
    def get(self):
        participants_str = request.args.get('participants')
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)

        if not participants_str or not year or not month:
            return {'error': 'Недостаточно данных (participants, year, month)'}, 400

        participant_ids = [int(pid) for pid in participants_str.split(',')]

        result = calculate_matches(participant_ids, year, month)

        return result

def calculate_matches(participant_ids, year, month):
    result = {}
    days_in_month = monthrange(year, month)[1]

    users = User.query.filter(User.id.in_(participant_ids)).all()
    user_privacy = {user.id: user.privacy_setting for user in users}
    user_names = {user.id: user.name for user in users}

    month_start = datetime(year, month, 1, 0, 0)
    month_end = datetime(year, month, days_in_month, 23, 59)

    events = (
        db.session.query(Event)
        .join(EventParticipant)
        .filter(
            EventParticipant.user_id.in_(participant_ids),
            Event.date_time >= month_start,
            Event.date_time <= month_end,
            Event.status == 'active'
        )
        .all()
    )

    user_events = {pid: [] for pid in participant_ids}
    for event in events:
        event_start = event.date_time
        event_end = event_start + timedelta(minutes=event.duration_minutes)
        for participant in event.participants:
            if participant.user_id in participant_ids:
                user_events[participant.user_id].append((event_start, event_end))

    for day in range(1, days_in_month + 1):
        day_start = datetime(year, month, day, 8, 0)
        day_end = datetime(year, month, day, 23, 59)

        user_free = {}
        for pid in participant_ids:
            if user_privacy.get(pid) == 'none':
                user_free[pid] = [(day_start, day_end)]
                continue

            busy = [
                (max(start, day_start), min(end, day_end))
                for start, end in user_events.get(pid, [])
                if end > day_start and start < day_end
            ]
            free = find_free_intervals(day_start, day_end, busy)
            user_free[pid] = free

        matches = []
        time = day_start
        while time + timedelta(hours=1) <= day_end:
            window_end = time + timedelta(hours=1)

            available_users = []
            for pid, slots in user_free.items():
                if any(slot_start <= time and slot_end >= window_end for slot_start, slot_end in slots):
                    available_users.append(user_names[pid])

            if available_users:
                matches.append({
                    'interval': f"{time.strftime('%H:%M')}-{window_end.strftime('%H:%M')}",
                    'users': available_users
                })

            time += timedelta(minutes=30)

        if any(len(m['users']) == len(participant_ids) for m in matches):
            color = 'green'
        elif any(m['users'] for m in matches):
            color = 'yellow'
        else:
            color = 'red'

        result[f"{year}-{month:02d}-{day:02d}"] = {
            'color': color,
            'matches': matches
        }

    return result

def find_free_intervals(day_start, day_end, busy_intervals):
    busy_intervals.sort()
    free_intervals = []
    current = day_start

    for start, end in busy_intervals:
        if start > current:
            free_intervals.append((current, start))
        if end > current:
            current = max(current, end)

    if current < day_end:
        free_intervals.append((current, day_end))

    return free_intervals
