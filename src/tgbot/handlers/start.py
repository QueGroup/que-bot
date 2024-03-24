from aiogram import Router, types
from aiogram.filters import CommandStart

start_router = Router()


@start_router.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Привет {user}".format(user=message.from_user.full_name))
