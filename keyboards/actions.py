from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def actions_before_finish():
    keyboard_actions = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton("Установить время оповещений")
    button2 = KeyboardButton("Посмотреть события запланированные на ближайшие n дней")
    keyboard_actions.add(button).add(button2)
    return keyboard_actions


def actions_for_run():
    keyboard_actions = actions_before_finish()
    button = KeyboardButton("Запустить бота")
    keyboard_actions.add(button)
    return keyboard_actions
