from aiogram.fsm.state import StatesGroup, State

class Steps(StatesGroup):
    ADD_EVENT = State()
    LOCATION = State()
    DESCRIPTION = State()
    TYPE_EVENT = State()
    EDIT_EVENT = State()
    DROP_EVENT = State()
