import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from os import getenv
from sys import exit
from create_calendar import get_calendar_service
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
service = get_calendar_service()
deleting_calendars = []
chat_ids = {}
list_calendar = service.calendarList().list().execute()['items']
list_events = []
for calendar in list_calendar:
    list_events.append(service.events().list(calendarId=calendar['id'],
                                             timeMin=(datetime.now() - timedelta(hours=3)).isoformat() + 'Z').execute()[
                           'items'])
print("list")
print(list_events)
minutes = None
