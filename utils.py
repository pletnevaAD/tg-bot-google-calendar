from create_bot import service

result = service.calendarList().list().execute()
length = len(result['items'])
list_calendar = []
for i in range(length):
    list_calendar.append(result['items'][i])
