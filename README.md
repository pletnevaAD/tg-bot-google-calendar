# Телеграм бот, оповещающий о событиях и изменениях в Google-календаре пользователя
## Описание
Телеграм-бота на Python, который выполняет запросы к Google Calendar 

Функциональность бота:
-	Возможность выбрать те календари, уведомление из которых пользователь не хотел бы получать;
- Просмотр событий на ближайшие N дней с названием, описанием, временем начала и ссылкой Join;
-	Уведомление пользователя об изменениях в календарях;
-	Уведомление пользователя о событиях за N минут (количество минут выбирает пользователь).

## Инструкция по запуску
- Чтобы создать бота, нам нужно дать ему название и адрес. 
  - Зайдите в Telegram под своим аккаунтом бота BotFather.
  - Нажмите кнопку «Запустить» (или отправим /start), в ответ BotFather пришлет вам список доступных команд.
  - Отправьте BotFather команду /newbot, чтобы создать нового бота. В ответ он попросит ввести имя будущего бота. После ввода имени нужно будет отправить адрес бота, он должен заканчиваться на слово bot. Если адрес будет уже кем‑то занят, придумайте что-то другое.

- Далее бот пришлет вам сообщение с токеном вашего бота. Сохраните его, чтобы потом использовать в скрипте бота.
- Далее в своей среде разработки в данном проекте в настройках конфигурации в переменных среды напишите BOT_TOKEN="полученный токен", чтобы создать экземпляр бота.
- Следующим шагом нужно получить client-secret.json, [вот тут]( https://karenapp.io/articles/how-to-automate-google-calendar-with-python-using-the-calendar-api/) в первых двух пунктах описано, как это сделать.
- Добавьте в свой проект файл client-secret.json.
- Можете запускать программу и пользоваться ботом!
