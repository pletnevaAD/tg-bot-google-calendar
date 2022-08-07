from enum import Enum
from aiogram.dispatcher.filters.state import State, StatesGroup


class StatesTime(StatesGroup):
    time = State()


class StateTimeForEdit(StatesGroup):
    time = State()


class StatesDays(StatesGroup):
    days = State()
