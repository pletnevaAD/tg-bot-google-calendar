from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard_actions = ReplyKeyboardMarkup()
button = KeyboardButton("Установить время оповещений")
button2 = KeyboardButton("Посмотреть события запланированные на ближайшие 7 дней")
keyboard_actions.add(button, button2)
