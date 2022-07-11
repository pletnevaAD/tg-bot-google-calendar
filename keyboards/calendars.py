import telegram as telegram
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import bold, italic
from utils import list_calendar


def genmarkup():
    keyboard_calendars1 = InlineKeyboardMarkup(row_width=2)
    length1 = len(list_calendar)
    for e in range(length1):
        button = InlineKeyboardButton(text=list_calendar[e]["summary"], callback_data="calendar_" + str(e))
        keyboard_calendars1.insert(button)
    keyboard_calendars1.add(
        InlineKeyboardButton(text="Вернуть удаленный календарь", callback_data="calendar_return"))
    keyboard_calendars1.add(InlineKeyboardButton(text="Закрыть", callback_data="calendar_close"))
    return keyboard_calendars1


def gen_del_markup(list_del_calendars):
    keyboard_calendars1 = InlineKeyboardMarkup(row_width=2)
    length1 = len(list_del_calendars)
    for e in range(length1):
        button = InlineKeyboardButton(text=list_del_calendars[e]["summary"], callback_data="delcalendar_" + str(e))
        keyboard_calendars1.insert(button)
    keyboard_calendars1.insert(InlineKeyboardButton(text="Закрыть", callback_data="delcalendar_close"))
    return keyboard_calendars1
