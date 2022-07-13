from aiogram.dispatcher.filters.state import State, StatesGroup


class StatesTime(StatesGroup):
    time = State()
