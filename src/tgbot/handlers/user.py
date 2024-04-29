from typing import (
    Any,
)

from aiogram import (
    F,
    Router,
    types,
)
from aiogram.filters import (
    Command,
)
from aiogram.fsm.context import (
    FSMContext,
)
from que_sdk import (
    QueClient,
)

from src.tgbot.keyboards import (
    reply,
)

user_router = Router()


@user_router.message(F.text == "👤 Аккаунт")
async def user_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()
    status_code, response = await que_client.get_user_me(access_token=storage.get("access_token"))
    days = response.get("days_since_created")
    text = (
        "Username: *{username}*\n"
        "TelegramID: `{telegram_id}`\n\n"
        "Вы с нами {days} дней"
    ).format(
        username=response.get("username"),
        telegram_id=response.get("telegram_id"),
        days=days
    )
    await message.answer(text=text)


@user_router.message(F.text, Command("reactivate"))
async def user_activate_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()
    access_token = storage.get("access_token")
    await que_client.reactivate_user(access_token=access_token)
    await message.delete()
    await message.answer(text="Поздравляем! Вы восстановили аккаунт", reply_markup=reply.main_menu())
