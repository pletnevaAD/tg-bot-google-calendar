import pprint
from datetime import datetime, timezone
import re

from deepdiff import DeepDiff, extract
from deepdiff.helper import CannotCompare

import create_bot
from account import Account


def get_my_events(account: Account, calendarId, timeMin, timeMax):
    result = account.service.events().list(calendarId=calendarId, timeMin=timeMin, timeMax=timeMax).execute()['items']
    return result


# def update_events_1(account: Account):  # сделать с привязкой к удаленному календарю
#     account.list_events.clear()
#     for calendar in account.list_calendar:
#         account.list_events.append(account.service.events().list(calendarId=calendar['id'],
#                                                                  timeMin=(
#                                                                              datetime.utcnow()).isoformat() + 'Z').execute()[
#                                        'items'])


def get_events(account: Account):
    result = []
    for calendar in account.list_calendar:
        result.append(account.service.events().list(calendarId=calendar['id'],
                                                    timeMin=(datetime.utcnow()).isoformat() + 'Z').execute()['items'])
    return result


def compare_func(x, y, level=None):
    try:
        return x['id'] == y['id']
    except Exception:
        raise CannotCompare() from None


async def update_calendar(account: Account):
    result = account.service.calendarList().list().execute()['items']
    ddiff = DeepDiff(account.list_calendar + account.deleting_calendars, result,
                     iterable_compare_func=compare_func)
    if ddiff:
        if 'iterable_item_added' in ddiff:
            for new_calendar_path in list(ddiff['iterable_item_added'].keys()):
                new_calendar = extract(result, new_calendar_path)
                account.list_calendar.append(new_calendar)
                account.list_events = get_events(account)
                await create_bot.bot.send_message(account.chat_id,
                                                  text="На сервере был добавлен календарь " + new_calendar['summary'] +
                                                       ". \nЕсли не хотите получать уведомления из этого календаря, "
                                                       "введите /start и уберите данный календарь")
        if 'iterable_item_removed' in ddiff:
            for removed_calendar_path in list(ddiff['iterable_item_removed'].keys()):
                m = re.search(r'\[([0-9]+)\]', removed_calendar_path)
                index_del = (int(m.group(1).replace('[', '').replace(']', '')))
                length_list = len(account.list_calendar)
                if index_del < length_list:
                    calendar_title = account.list_calendar[index_del]['summary']
                    account.list_calendar.pop(index_del)
                    account.list_events = get_events(account)
                    await create_bot.bot.send_message(account.chat_id,
                                                      text="На сервере был удален календарь " +
                                                           calendar_title)
                    print("эвэйтнули")

                else:
                    calendar_title = account.deleting_calendars[index_del - length_list]['summary']
                    account.deleting_calendars.pop(index_del - length_list)
                    await create_bot.bot.send_message(account.chat_id,
                                                      text="На сервере был удален календарь " +
                                                           calendar_title)
        if 'values_changed' in ddiff:
            for changed_calendar_path in list(ddiff['values_changed'].keys()):
                m = re.search(r'\[([0-9]+)\]', changed_calendar_path)
                index_change = (int(m.group(1).replace('[', '').replace(']', '')))
                length_list = len(account.list_calendar)
                if index_change < length_list:
                    before_title = account.list_calendar[index_change]['summary']
                    result_item = None
                    for item in result:
                        if item['id'] == account.list_calendar[index_change]['id']:
                            result_item = item
                    listok = account.list_calendar
                    account.list_calendar.pop(index_change)
                    account.list_calendar.insert(index_change, result_item)
                    account.list_events = get_events(account)
                    print("SOS____________\n", DeepDiff(listok, account.list_calendar))
                    if result_item['summary'] != before_title:
                        await create_bot.bot.send_message(account.chat_id,
                                                          text="Название календаря " +
                                                               before_title + " было поменяно на " +
                                                               result_item['summary'])

                else:
                    result_item = None
                    for item in result:
                        if item['id'] == account.deleting_calendars[index_change - length_list]['id']:
                            result_item = item
                    account.deleting_calendars.pop(index_change - length_list)
                    account.deleting_calendars.insert(index_change - length_list, result_item)


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


async def update_events(account: Account):
    result = get_events(account)
    ddiff = DeepDiff(account.list_events, result, iterable_compare_func=compare_func)
    # pprint.pprint(ddiff)
    if ddiff:
        if 'iterable_item_added' in ddiff:
            for new_event_path in list(ddiff['iterable_item_added'].keys()):
                new_event = extract(result, new_event_path)
                m = re.search(r'\[([0-9]+)\]', new_event_path)
                index_calendar = (int(m.group(1).replace('[', '').replace(']', '')))
                account.list_events[index_calendar].append(new_event)
                await create_bot.bot.send_message(account.chat_id,
                                                  text="На сервере было добавлено:\n" +
                                                       get_events_description(new_event))
        if 'iterable_item_removed' in ddiff:
            for removed_event_path in list(ddiff['iterable_item_removed'].keys()):
                del_event = extract(account.list_events, removed_event_path)
                index_del = re.findall(r'\[([0-9]+)\]', removed_event_path)
                account.list_events[int(index_del[0])].pop(int(index_del[1]))
                await create_bot.bot.send_message(account.chat_id,
                                                  text="На сервере было удалено:\n " +
                                                       get_events_description(del_event))
        if 'values_changed' in ddiff:
            for changed_calendar_path in list(ddiff['values_changed'].keys()):

                result_item = None
                index_change = re.findall(r'\[([0-9]+)\]', changed_calendar_path)
                for calendar in result:
                    for item in calendar:
                        if item['id'] == account.list_events[int(index_change[0])][int(index_change[1])]['id']:
                            result_item = item
                before_item = account.list_events[int(index_change[0])][int(index_change[1])]
                account.list_events[int(index_change[0])].pop(int(index_change[1]))
                account.list_events[int(index_change[0])].insert(int(index_change[1]), result_item)
                if get_events_description(result_item) != get_events_description(before_item):
                    await create_bot.bot.send_message(account.chat_id,
                                                      text="Обновлено\n" + get_events_description(
                                                          before_item) + "на\n" + get_events_description(
                                                          result_item))


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
