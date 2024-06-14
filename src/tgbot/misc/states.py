from aiogram.fsm import (
    state,
)


class RegistrationSG(state.StatesGroup):
    first_name = state.State()
    gender = state.State()
    city = state.State()
    birthday = state.State()
    about_me = state.State()
    interested_in = state.State()
    hobbies = state.State()
    photos = state.State()
