from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import create_bot
from account import Account
from utils import fun


def genmarkup(account: Account):
    keyboard_calendars1 = InlineKeyboardMarkup(row_width=2)
    account.list_calendar.clear()
    account.list_calendar.extend(fun(account))
    length1 = len(account.list_calendar)
    length2 = len(account.deleting_calendars)
    for i in account.deleting_calendars:
        for k in account.list_calendar:
            if (i['id']) == (k['id']):
                account.list_calendar.pop(account.list_calendar.index(k))
                length1 = length1 - 1
    for e in range(length1):
        button = InlineKeyboardButton(text=account.list_calendar[e]["summary"], callback_data="calendar_" + str(e))
        keyboard_calendars1.insert(button)
    keyboard_calendars1.add(
        InlineKeyboardButton(text="Вернуть удаленный календарь", callback_data="calendar_return"))
    keyboard_calendars1.add(InlineKeyboardButton(text="Готово", callback_data="calendar_close"))
    return keyboard_calendars1


def gen_del_markup(list_del_calendars):
    keyboard_calendars1 = InlineKeyboardMarkup(row_width=2)
    length1 = len(list_del_calendars)
    for e in range(length1):
        button = InlineKeyboardButton(text=list_del_calendars[e]["summary"], callback_data="delcalendar_" + str(e))
        keyboard_calendars1.insert(button)
    keyboard_calendars1.insert(InlineKeyboardButton(text="Готово", callback_data="delcalendar_close"))
    return keyboard_calendars1
