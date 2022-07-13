import datetime
import json
import re
import time

import dateutil
import flask

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from create_bot import dp, bot, service, deleting_calendars
from states import StatesTime
from keyboards.calendars import list_calendar
from keyboards import calendars, actions
from utils import get_my_events

minutes = 0.1


# @dp.message_handler(commands="start")
async def command_start(message: types.Message, state: None):
    name = [message.from_user.first_name, message.from_user.last_name]
    name = ' '.join(filter(None, name))
    await bot.send_message(message.from_user.id, "Привет, " + name + "!" + " Этот бот поможет не забыть тебе о "
                                                                           "событиях из твоего Google-календаря. "
                                                                           "Приятного использования!")
    await bot.send_message(message.from_user.id,
                           "Выберите календари, уведомления о событиях которых вы НЕ хотели бы получать",
                           reply_markup=calendars.genmarkup())


@dp.message_handler(text="Установить время оповещений")
async def fun(message: types.Message, state: None):
    await StatesTime.time.set()
    await message.answer("За какое время до начала событий вы хотите получать уведомления о них?",
                         reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=StatesTime.time)
async def get_minutes(message: types.Message, state: FSMContext):
    global minutes
    minutes = message.text
    if re.match(r'^-?\d+(?:\.\d+)?$', minutes) is None:
        await message.answer("Введите число! Если число дробное, то дробную часть отделите точкой.")
    else:
        local_time = float(minutes)
        local_time = local_time * 60
        await message.answer("Все ок вот ваш тайм: " + str(local_time))
        await state.finish()


def get_calendar_and_title(number):
    calendar_whole = list_calendar[number]
    calendar_title = calendar_whole["summary"]
    return calendar_whole, calendar_title


async def update_keyboard(message: types.Message, text: str):
    # Общая функция для обновления текста с отправкой той же клавиатуры
    await message.edit_text(text + "Выберите календари, уведомления о событиях которых вы НЕ хотели бы получать",
                            reply_markup=calendars.genmarkup())


async def update_deleting_keyboard(message: types.Message, text: str):
    # Общая функция для обновления текста с отправкой той же клавиатуры
    await message.edit_text(text + "Выберите календари, которые вы хотите вернуть",
                            reply_markup=calendars.gen_del_markup(deleting_calendars))


@dp.callback_query_handler(Text(startswith="calendar_"))
async def callbacks_num(call: types.CallbackQuery):
    action = call.data.split("_")[1]
    length = len(list_calendar)
    if action == "close":
        list_title = []
        for i in range(length):
            list_title.append(list_calendar[i]['summary'])
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text="Вы успешно выбрали календари. Вот список календарей:")
        await bot.send_message(chat_id=call.from_user.id, text='\n'.join(list_title))
        await bot.send_message(chat_id=call.from_user.id, text="Выберите действие",
                               reply_markup=actions.keyboard_actions)
    elif action == "return":
        if len(deleting_calendars) == 0:
            await call.answer(text='Нет удаленных календарей')
        else:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.from_user.id,
                                   text="Выберите календари, которые вы хотите вернуть",
                                   reply_markup=calendars.gen_del_markup(deleting_calendars))

    else:
        for i in range(length):
            if action == str(i):
                calendar_whole, calendar_title = get_calendar_and_title(i)
                deleting_calendars.append(list_calendar.pop(i))
                await update_keyboard(call.message, calendar_title + " успешно удален. ")
    await call.answer()


@dp.callback_query_handler(Text(startswith="delcalendar_"))
async def callbacks_del(call: types.CallbackQuery):
    action = call.data.split("_")[1]
    length = len(deleting_calendars)
    if action == "close":
        await update_keyboard(call.message, "")
    else:
        for i in range(length):
            if action == str(i):
                inserting_calendar = deleting_calendars.pop(i)
                list_calendar.append(inserting_calendar)
                await update_deleting_keyboard(call.message, inserting_calendar['summary'] + " успешно возвращен. ")

    await call.answer()


@dp.message_handler(text="Посмотреть события запланированные на ближайшие 7 дней")
async def get_events(message: types.Message):
    length = len(list_calendar)
    for i in range(length):
        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(days=7)
        await message.answer("События в календаре " + list_calendar[i]['summary'] + ":")
        result = get_my_events(calendarId=list_calendar[i]["id"], timeMin=start_date.isoformat() + 'Z',
                               timeMax=end_date.isoformat() + 'Z')
        leng = len(result['items'])
        print(result)
        list_events = []
        if leng == 0:
            await message.answer("Календарь пуст")
        else:
            for j in range(leng):
                event_descr = "Событие: " + result['items'][j]['summary'] + "\n"
                if 'description' in result['items'][j]:
                    event_descr += "Описание: " + result['items'][j]['description'] + "\n"
                event_descr += "Время начала:  " \
                               + str(datetime.datetime.fromisoformat(result['items'][j]['start']['dateTime'])) + "\n"
                if 'hangoutLink' in result['items'][j]:
                    event_descr += "Присоединиться: " + result['items'][j]['hangoutLink'] + "\n"
                list_events.append(event_descr)
            await message.answer("\n".join(list_events) + "\n")


async def command_other(message: types.Message):
    name = [message.from_user.first_name, message.from_user.last_name]
    name = ' '.join(filter(None, name))
    await message.answer("Я обязательно отвечу на твое сообщение, но не сегодня, " + name + "!")


def register_handlers_user(dp: Dispatcher):
    dp.register_message_handler(command_start, commands="start")
    # dp.register_callback_query_handler(callbacks_num, Text(startswith="calendar_"))
    # dp.register_callback_query_handler(callbacks_del, Text(startswith="delcalendar_"))
    # dp.register_message_handler(get_events, commands="получить")
    dp.register_message_handler(command_other)
