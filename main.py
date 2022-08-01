from aiogram.utils import executor
from create_bot import dp
from handlers import user
from utils import set_default_commands

user.register_handlers_user(dp)

async def on_startup(dp):
    await set_default_commands(dp)

if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
