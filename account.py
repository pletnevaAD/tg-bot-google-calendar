import pprint
from datetime import datetime

from create_calendar import get_calendar_service


class Account:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.run = 0
        self.service = get_calendar_service()
        self.deleting_calendars = []
        self.list_calendar = self.service.calendarList().list().execute()['items']
        self.list_events = []
        for calendar in self.list_calendar:
            self.list_events.append(self.service.events().list(calendarId=calendar['id'],
                                                     timeMin=(datetime.utcnow()).isoformat() + 'Z').execute()['items'])
        self.minutes = None
