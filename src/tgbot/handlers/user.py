from aiogram import Router, F, types

user_router = Router()


@user_router.message(F.text == "👤 Аккаунт")
async def user_handler(message: types.Message):
    await message.answer(text="Информация о пользователе")
