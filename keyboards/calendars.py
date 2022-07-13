import telegram as telegram
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import bold, italic
from utils import fun
from create_bot import deleting_calendars, list_calendar


def genmarkup():
    keyboard_calendars1 = InlineKeyboardMarkup(row_width=2)
    list_calendar.clear()
    list_calendar.extend(fun())
    length1 = len(list_calendar)
    length2 = len(deleting_calendars)
    for i in deleting_calendars:
        for e in list_calendar:
            if (i['id']) == (e['id']):
                list_calendar.pop(list_calendar.index(e))
                length1 = length1 - 1
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
