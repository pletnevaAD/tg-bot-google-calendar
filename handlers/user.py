import json
import flask

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from create_bot import dp, bot, service
from utils import list_calendar
from keyboards import calendars


# @dp.message_handler(commands="start")
async def command_start(message: types.Message):
    name = [message.from_user.first_name, message.from_user.last_name]
    name = ' '.join(filter(None, name))
    await bot.send_message(message.from_user.id, "Привет, " + name + "!" + " Этот бот поможет не забыть тебе о "
                                                                           "событиях из твоего Google-календаря. "
                                                                           "Приятного использования!")
    await bot.send_message(message.from_user.id,
                           "Выберите календари, уведомления о событиях которых вы НЕ хотели бы получать",
                           reply_markup=calendars.genmarkup())


def get_calendar_and_title(number):
    calendar_whole = list_calendar[number]
    calendar_title = calendar_whole["summary"]
    return calendar_whole, calendar_title


async def update_keyboard(message: types.Message, text: str):
    # Общая функция для обновления текста с отправкой той же клавиатуры
    await message.edit_text(text + "Выберите календари, уведомления о событиях которых вы НЕ хотели бы получать",
                            reply_markup=calendars.genmarkup())


deleting_calendars = []


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
#
#
# @dp.message_handler(commands="event")
# async def get_events(message: types.Message):
#     result = service.events().list(calendarId=list_calendar[0]["id"]).execute()
#     title = str(result['items'][0]['summary'])
#     leng = len(result['items'])
#     for i in range(leng):
#         await message.answer(list_calendar[0]['summary'])
#         await message.answer(result['items'][i]['summary'])
#


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
