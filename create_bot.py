import logging
from aiogram import Bot, Dispatcher
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
list_calendar = []
