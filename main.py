from aiogram.utils import executor
from create_bot import dp
from handlers import user

user.register_handlers_user(dp)

if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
