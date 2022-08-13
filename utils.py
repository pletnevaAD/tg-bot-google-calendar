from datetime import datetime, timezone

import create_bot
from account import Account


def fun(account: Account):
    result = account.service.calendarList().list().execute()
    length = len(result['items'])
    local_list_calendar = []
    for i in range(length):
        local_list_calendar.append(result['items'][i])
    return local_list_calendar


def get_my_events(account: Account, calendarId, timeMin, timeMax):
    result = account.service.events().list(calendarId=calendarId, timeMin=timeMin, timeMax=timeMax).execute()['items']
    return result


def update_events(account: Account): #сделать с привязкой к удаленному календарю
    account.list_events.clear()
    for calendar in account.list_calendar:
        account.list_events.append(account.service.events().list(calendarId=calendar['id'],
                                                                 timeMin=(
                                                                             datetime.utcnow()).isoformat() + 'Z').execute()[
                                       'items'])


async def get_new_calendar(account: Account):
    result = account.service.calendarList().list().execute()['items']
    length_now = len(result)
    length_prev = len(account.list_calendar) + len(account.deleting_calendars)
    if length_now != length_prev:
        if length_now < length_prev:
            for index, item in enumerate(list(account.list_calendar)):
                if item not in result:
                    account.list_calendar.pop(index)
                    await create_bot.bot.send_message(account.chat_id,
                                                      text="На сервере был удален календарь " + item['summary'])
            for index, item in enumerate(list(account.deleting_calendars)):
                if item not in result:
                    account.deleting_calendars.pop(index)
                    await create_bot.bot.send_message(account.chat_id,
                                                      text="На сервере был удален календарь " + item['summary'])
        else:
            for item in result:
                if item not in (list(account.list_calendar) + list(account.deleting_calendars)):
                    account.list_calendar.append(item)
                    await create_bot.bot.send_message(account.chat_id,
                                                      text="На сервере был добавлен календарь " + item['summary'] +
                                                           ". \nЕсли не хотите получать уведомления из этого календаря, "
                                                           "введите /start и уберите данный календарь")

    else:
        if result != account.list_calendar + account.deleting_calendars:
            for item_result in result:
                if item_result not in (list(account.list_calendar) + list(account.deleting_calendars)):
                    for index, item in enumerate(list(account.deleting_calendars)):
                        if item not in result:
                            account.deleting_calendars.pop(index)
                            account.deleting_calendars.append(item_result)
                            if item_result['summary'] != item['summary']:
                                await create_bot.bot.send_message(account.chat_id,
                                                                  text="Название календаря " + item[
                                                                      'summary'] + " было поменяно на " +
                                                                       item_result[
                                                                           'summary'])
                            else:
                                return
                    for index, item in enumerate(list(account.list_calendar)):
                        if item not in result:
                            account.list_calendar.pop(index)
                            account.list_calendar.append(item_result)
                            if item_result['summary'] != item['summary']:
                                await create_bot.bot.send_message(account.chat_id,
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


async def get_new_events(account: Account):
    result = []
    # print(account.list_calendar)
    for calendar in account.list_calendar:
        result.append(account.service.events().list(calendarId=calendar['id'],
                                                    timeMin=(datetime.utcnow()).isoformat() + 'Z').execute()['items'])
    if result != account.list_events:
        length_result = len(result)
        for i in range(length_result):
            if result[i] != account.list_events[i]:
                length_now = len(result[i])
                length_prev = len(account.list_events[i])
                if length_now != length_prev:
                    if length_now < length_prev:
                        for index, item in enumerate(list(account.list_events[i])):
                            if item not in result[i]:
                                account.list_events[i].pop(index)
                                await create_bot.bot.send_message(account.chat_id,
                                                                  text="На сервере было удалено:\n " +
                                                                       get_events_description(item))
                    elif length_now > length_prev:
                        for item in result[i]:
                            if item not in account.list_events[i]:
                                account.list_events[i].append(item)
                                await create_bot.bot.send_message(account.chat_id,
                                                                  text="На сервере было добавлено:\n" +
                                                                       get_events_description(item))
                else:
                    for item_result in result[i]:
                        if item_result not in account.list_events[i]:
                            for index, item in enumerate(list(account.list_events[i])):
                                if item not in result[i]:
                                    account.list_events[i].pop(index)
                                    account.list_events[i].append(item_result)
                                    if get_events_description(item) != get_events_description(item_result):
                                        await create_bot.bot.send_message(account.chat_id,
                                                                          text="Обновлено\n" + get_events_description(
                                                                              item) + "на\n" + get_events_description(
                                                                              item_result))
    else:
        return


async def get_event_in_time(account: Account):
    if account.minutes != None:
        for i in range(len(account.list_events)):
            for j in range(len(account.list_events[i])):
                if 'dateTime' in account.list_events[i][j]['start']:
                    delta = ((datetime.fromisoformat(
                        account.list_events[i][j]['start']['dateTime']).replace(
                        tzinfo=timezone.utc) - datetime.now().replace(
                        tzinfo=timezone.utc)).total_seconds()) / 60.0
                    if 0 <= (float(account.minutes) - delta) <= 3.1 / 60.0:
                        await create_bot.bot.send_message(account.chat_id,
                                                          text="Через " + account.minutes + " минут!\n"
                                                               + get_events_description(
                                                              account.list_events[i][j]))
                if 'date' in account.list_events[i][j]['start']:
                    delta = (datetime.fromisoformat(
                        account.list_events[i][j]['start']['date']).replace(
                        tzinfo=timezone.utc) - datetime.now().replace(
                        tzinfo=timezone.utc)).total_seconds() / 60.0
                    if 0 <= (float(account.minutes) - delta) <= 3.1 / 60.0:
                        await create_bot.bot.send_message(account.chat_id,
                                                          text="Через " + account.minutes + " минут!"
                                                               + get_events_description(
                                                              account.list_events[i][j]))
