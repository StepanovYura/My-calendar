from flask_restful import Resource
from models.models import Event
from extensions import db
from flask import request
from datetime import datetime

class EventList(Resource):
    def get(self):
        events = Event.query.all()
        return [{
            'id': e.id,
            'title': e.title,
            'description': e.description,
            'date_time': e.date_time.isoformat()
        } for e in events]
