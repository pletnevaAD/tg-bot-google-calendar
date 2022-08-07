from datetime import datetime, timezone, time, timedelta

from aiogram import types

import create_bot
from create_bot import service, list_calendar, deleting_calendars, list_events


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("edit", "Запустить бота")
    ])


def fun():
    result = service.calendarList().list().execute()
    length = len(result['items'])
    local_list_calendar = []
    for i in range(length):
        local_list_calendar.append(result['items'][i])
    return local_list_calendar


def get_my_events(calendarId, timeMin, timeMax):
    result = service.events().list(calendarId=calendarId, timeMin=timeMin, timeMax=timeMax).execute()['items']
    return result


async def get_new_calendar():
    result = service.calendarList().list().execute()['items']
    length_now = len(result)
    length_prev = len(list_calendar) + len(deleting_calendars)
    if length_now != length_prev:
        if length_now < length_prev:
            for index, item in enumerate(list(list_calendar)):
                if item not in result:
                    list_calendar.pop(index)
                    for id in create_bot.chat_ids:
                        await create_bot.bot.send_message(id,
                                                          text="На сервере был удален календарь " + item['summary'])
            for index, item in enumerate(list(deleting_calendars)):
                if item not in result:
                    deleting_calendars.pop(index)
                    for id in create_bot.chat_ids:
                        await create_bot.bot.send_message(id,
                                                          text="На сервере был удален календарь " + item['summary'])
        else:
            for item in result:
                if item not in (list(list_calendar) + list(deleting_calendars)):
                    list_calendar.append(item)
                    for id in create_bot.chat_ids:
                        await create_bot.bot.send_message(id,
                                                          text="На сервере был добавлен календарь " + item['summary'] +
                                                               ". \nЕсли не хотите получать уведомления из этого календаря, "
                                                               "введите /start и уберите данный календарь")
    else:
        if result != list_calendar + deleting_calendars:
            for item_result in result:
                if item_result not in (list(list_calendar) + list(deleting_calendars)):
                    for index, item in enumerate(list(deleting_calendars)):
                        if item not in result:
                            deleting_calendars.pop(index)
                            deleting_calendars.append(item_result)
                            if item_result['summary'] != item['summary']:
                                for id in create_bot.chat_ids:
                                    await create_bot.bot.send_message(id,
                                                                      text="Название календаря " + item[
                                                                          'summary'] + " было поменяно на " +
                                                                           item_result[
                                                                               'summary'])
                            else:
                                return
                    for index, item in enumerate(list(list_calendar)):
                        if item not in result:
                            list_calendar.pop(index)
                            list_calendar.append(item_result)
                            if item_result['summary'] != item['summary']:
                                for id in create_bot.chat_ids:
                                    await create_bot.bot.send_message(id,
                                                                      text="Название календаря " + item[
                                                                          'summary'] + " было поменяно на " +
                                                                           item_result[
                                                                               'summary'])
                            else:
                                return
    return


def get_events_description(item):
    event_descr = ""
    if 'summary' in item:
        event_descr += "Событие: " + item['summary'] + "\n"
    else:
        event_descr += "Событие: " + "без названия" + "\n"
    if 'description' in item:
        event_descr += "Описание: " + item['description'] + "\n"
    if 'dateTime' in item['start']:
        event_descr += "Время начала:  " \
                       + str(
            datetime.fromisoformat(item['start']['dateTime'])) + "\n"
    if 'date' in item['start']:
        event_descr += "Дата начала:  " \
                       + str(
            datetime.fromisoformat(item['start']['date'])) + "\n"
    if 'hangoutLink' in item:
        event_descr += "Присоединиться: " + item['hangoutLink'] + "\n"
    return event_descr


async def get_new_events():
    result = []
    for calendar in list_calendar:
        result.append(service.events().list(calendarId=calendar['id'],
                                            timeMin=(datetime.utcnow()).isoformat() + 'Z').execute()['items'])
    if result != list_events:
        length_result = len(result)
        for i in range(length_result):
            if result[i] != list_events[i]:
                length_now = len(result[i])
                length_prev = len(list_events[i])
                if length_now != length_prev:
                    if length_now < length_prev:
                        for index, item in enumerate(list(list_events[i])):
                            if item not in result[i]:
                                list_events[i].pop(index)
                                for id in create_bot.chat_ids:
                                    await create_bot.bot.send_message(id,
                                                                      text="На сервере было удалено:\n " +
                                                                           get_events_description(item))
                    elif length_now > length_prev:
                        for item in result[i]:
                            if item not in list_events[i]:
                                list_events[i].append(item)
                                for id in create_bot.chat_ids:
                                    await create_bot.bot.send_message(id,
                                                                      text="На сервере было добавлено:\n" +
                                                                           get_events_description(item))
                else:
                    for item_result in result[i]:
                        if item_result not in list_events[i]:
                            for index, item in enumerate(list(list_events[i])):
                                if item not in result[i]:
                                    list_events[i].pop(index)
                                    list_events[i].append(item_result)
                                    if get_events_description(item) != get_events_description(item_result):
                                        for id in create_bot.chat_ids:
                                            await create_bot.bot.send_message(id,
                                                                              text="Обновлено\n" + get_events_description(
                                                                                  item) + "на\n" + get_events_description(
                                                                                  item_result))
    else:
        return


async def get_event_in_time():
    if create_bot.minutes != None:
        for i in range(len(list_events)):
            for j in range(len(list_events[i])):
                if 'dateTime' in list_events[i][j]['start']:
                    delta = ((datetime.fromisoformat(
                        list_events[i][j]['start']['dateTime']).replace(tzinfo=timezone.utc) - datetime.now().replace(
                        tzinfo=timezone.utc)).total_seconds()) / 60.0
                    if 0 <= (float(create_bot.minutes) - delta) <= 3.1 / 60.0:
                        for id in create_bot.chat_ids:
                            await create_bot.bot.send_message(id,
                                                              text="Через " + create_bot.minutes + " минут!\n"
                                                                   + get_events_description(
                                                                  list_events[i][j]))
                if 'date' in list_events[i][j]['start']:
                    delta = (datetime.fromisoformat(
                        list_events[i][j]['start']['date']).replace(tzinfo=timezone.utc) - datetime.now().replace(
                        tzinfo=timezone.utc)).total_seconds() / 60.0
                    if 0 <= (float(create_bot.minutes) - delta) <= 3.1 / 60.0:
                        for id in create_bot.chat_ids:
                            await create_bot.bot.send_message(id,
                                                              text="Через " + create_bot.minutes + " минут!"
                                                                   + get_events_description(
                                                                  list_events[i][j]))
