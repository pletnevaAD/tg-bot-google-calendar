import logging
import pprint
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher, types
from os import getenv
from sys import exit

from dateutil.tz import tzlocal

from account import Account
from create_calendar import get_calendar_service
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tzlocal import get_localzone

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
account = []
# service = get_calendar_service()
# deleting_calendars = []
# chat_ids = {}
# list_calendar = service.calendarList().list().execute()['items']
# list_events = []
# for calendar in list_calendar:
#     list_events.append(service.events().list(calendarId=calendar['id'],
#                                              timeMin=(datetime.utcnow()).isoformat() + 'Z').execute()['items'])
# minutes = None
