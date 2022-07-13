from create_bot import service


def fun():
    result = service.calendarList().list().execute()
    length = len(result['items'])
    list_calendar = []
    for i in range(length):
        list_calendar.append(result['items'][i])
    return list_calendar


def get_my_events(calendarId, timeMin, timeMax):
    result = service.events().list(calendarId=calendarId, timeMin=timeMin, timeMax=timeMax).execute()
    return result
