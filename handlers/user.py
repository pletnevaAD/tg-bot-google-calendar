import asyncio
import datetime
import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

import utils
import create_bot
from keyboards import calendars, actions
from keyboards.calendars import list_calendar
from states import StatesTime, StatesDays, StateTimeForEdit
from utils import get_my_events

days_amount = None


# @dp.message_handler(commands="start")
async def command_start(message: types.Message, state: None):
    name = [message.from_user.first_name, message.from_user.last_name]
    name = ' '.join(filter(None, name))
    create_bot.chat_ids[message.from_user.id] = message.from_user
    await create_bot.bot.send_message(message.from_user.id,
                                      "Привет, " + name + "!" + " Этот бот поможет не забыть тебе о "
                                                                "событиях из твоего Google-календаря. "
                                                                "Приятного использования!")
    await create_bot.bot.send_message(message.from_user.id,
                                      "Выберите календари, уведомления о событиях которых вы НЕ хотели бы получать",
                                      reply_markup=calendars.genmarkup())


async def func():
    while True:
        await utils.get_new_calendar()
        await utils.get_new_events()
        await utils.get_event_in_time()
        await asyncio.sleep(3)


# @create_bot.dp.message_handler(text="Запустить бота")
async def run_bot(message: types.Message):
    loop = asyncio.get_event_loop()
    loop.create_task(func())
    await message.answer("Вы успешно запустили бота!", reply_markup=actions.actions_after_run())


# @create_bot.dp.message_handler(text="Установить время оповещений")
async def time_question(message: types.Message, state: None):
    await StatesTime.time.set()
    await message.answer("За какое время(в минутах) до начала событий вы хотите получать уведомления о них?")


# @create_bot.dp.message_handler(text="Изменить время оповещений")
async def time_question_edit(message: types.Message, state: None):
    await StateTimeForEdit.time.set()
    await message.answer("За какое время(в минутах) до начала событий вы хотите получать уведомления о них?")


# @create_bot.dp.message_handler(state=StatesTime.time)
async def get_minutes(message: types.Message, state: FSMContext):
    create_bot.minutes = message.text
    if re.match(r'^-?\d+(?:\.\d+)?$', create_bot.minutes) is None:
        await message.answer("Введите число! Если число дробное, то дробную часть отделите точкой.")
    else:
        local_time = float(create_bot.minutes)
        await message.answer("Вы будете получать уведомление за " + str(local_time) + " минут до события",
                             reply_markup=actions.actions_for_run())
        await state.finish()


# @create_bot.dp.message_handler(state=StateTimeForEdit.time)
async def get_minutes_edit(message: types.Message, state: FSMContext):
    create_bot.minutes = message.text
    if re.match(r'^-?\d+(?:\.\d+)?$', create_bot.minutes) is None:
        await message.answer("Введите число! Если число дробное, то дробную часть отделите точкой.")
    else:
        local_time = float(create_bot.minutes)
        await message.answer("Время оповещений было изменено. Вы будете получать уведомление за " + str(
            local_time) + " минут до события", reply_markup=actions.actions_after_run())
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
                            reply_markup=calendars.gen_del_markup(create_bot.deleting_calendars))


# @create_bot.dp.callback_query_handler(Text(startswith="calendar_"))
async def callbacks_num(call: types.CallbackQuery):
    action = call.data.split("_")[1]
    length = len(list_calendar)
    if action == "close":
        list_title = []
        for i in range(length):
            list_title.append(list_calendar[i]['summary'])
        await create_bot.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await create_bot.bot.send_message(chat_id=call.from_user.id,
                                          text="Вы успешно выбрали календари. Вот список календарей:")
        await create_bot.bot.send_message(chat_id=call.from_user.id, text='\n'.join(list_title))
        await create_bot.bot.send_message(chat_id=call.from_user.id, text="Выберите действие",
                                          reply_markup=actions.actions_before_finish())
    elif action == "return":
        if len(create_bot.deleting_calendars) == 0:
            await call.answer(text='Нет удаленных календарей')
        else:
            await create_bot.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await create_bot.bot.send_message(chat_id=call.from_user.id,
                                              text="Выберите календари, которые вы хотите вернуть",
                                              reply_markup=calendars.gen_del_markup(create_bot.deleting_calendars))

    else:
        for i in range(length):
            if action == str(i):
                calendar_whole, calendar_title = get_calendar_and_title(i)
                create_bot.deleting_calendars.append(list_calendar.pop(i))
                await update_keyboard(call.message, calendar_title + " успешно удален. ")
    await call.answer()


# @create_bot.dp.callback_query_handler(Text(startswith="delcalendar_"))
async def callbacks_del(call: types.CallbackQuery):
    action = call.data.split("_")[1]
    length = len(create_bot.deleting_calendars)
    if action == "close":
        await update_keyboard(call.message, "")
    else:
        for i in range(length):
            if action == str(i):
                inserting_calendar = create_bot.deleting_calendars.pop(i)
                list_calendar.append(inserting_calendar)
                await update_deleting_keyboard(call.message, inserting_calendar['summary'] + " успешно возвращен. ")

    await call.answer()


# @create_bot.dp.message_handler(text="Посмотреть события запланированные на ближайшие n дней")
async def get_days(message: types.Message, state: None):
    await StatesDays.days.set()
    await message.answer("На сколько дней вперед вы хотите посмотреть запланированные события?")


# @create_bot.dp.message_handler(state=StatesDays.days)
async def get_events(message: types.Message, state: FSMContext):
    global days_amount
    days_amount = message.text
    if re.match(r'^\d+?$', days_amount) is None:
        await message.answer("Введите целое число!")
    else:
        length = len(list_calendar)
        for i in range(length):
            start_date = datetime.datetime.utcnow()
            end_date = start_date + datetime.timedelta(days=int(days_amount))
            await message.answer("События в календаре " + list_calendar[i]['summary'] + ":")
            result = get_my_events(calendarId=list_calendar[i]["id"], timeMin=start_date.isoformat() + 'Z',
                                   timeMax=end_date.isoformat() + 'Z')
            leng = len(result)
            list_events = []
            if leng == 0:
                await message.answer("Календарь пуст")
            else:
                for j in range(leng):
                    list_events.append(utils.get_events_description(result[j]))
                await message.answer("\n".join(list_events) + "\n")
        await state.finish()


async def command_help(message: types.Message):
    await message.answer(
        "Возможности бота:\nНажмите на /start, чтобы настроить и запустить бота." +
        " Вы можете выбрать нужные Вам календари, уведомления о событиях которых, Вы хотите получать." +
        " Затем настройте время оповещений от бота (в любой момент его можно изменить)." +
        " После этого нажмите кнопку \" Запустить бота \"." +
        " Также в любой момент вы можете посмотреть события на желаемое количество дней вперед." +
        "\nПриятного использования!")


async def command_other(message: types.Message):
    name = [message.from_user.first_name, message.from_user.last_name]
    name = ' '.join(filter(None, name))
    await message.answer(name + ", нажмите на /start, чтобы заново выбрать календари и установить время оповещений!")


def register_handlers_user(dp: Dispatcher):
    dp.register_message_handler(command_start, commands="start")
    dp.register_message_handler(run_bot, text="Запустить бота")
    dp.register_message_handler(time_question, text="Установить время оповещений")
    dp.register_message_handler(time_question_edit, text="Изменить время оповещений")
    dp.register_message_handler(get_minutes, state=StatesTime.time)
    dp.register_message_handler(get_minutes_edit, state=StateTimeForEdit.time)
    dp.register_callback_query_handler(callbacks_num, Text(startswith="calendar_"))
    dp.register_callback_query_handler(callbacks_del, Text(startswith="delcalendar_"))
    dp.register_message_handler(get_events, state=StatesDays.days)
    dp.register_message_handler(get_days, text="Посмотреть события запланированные на ближайшие n дней")
    dp.register_message_handler(command_help, commands="help")
    dp.register_message_handler(command_other)
