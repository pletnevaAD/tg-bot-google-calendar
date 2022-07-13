from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard_actions = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton("Установить время оповещений")
button2 = KeyboardButton("Посмотреть события запланированные на ближайшие n дней")
keyboard_actions.add(button).add(button2)
