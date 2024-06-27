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
    StateFilter,
)
from aiogram.fsm.context import (
    FSMContext,
)
from que_sdk import (
    QueClient,
)

from src.tgbot.filters import (
    ChatTypeFilter,
)
from src.tgbot.keyboards import (
    inline,
    reply,
)
from src.tgbot.misc import (
    states,
)

user_router = Router()
user_router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


@user_router.message(F.text == "👤 Аккаунт")
@user_router.message(F.text == "<< Вернуться назад", StateFilter(states.RegistrationSG.first_name))
@user_router.callback_query(F.data == "back_to_user_menu")
async def user_handler(obj: types.TelegramObject, state: FSMContext, **middleware_data: Any) -> None:
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()
    user = storage.get("user")
    if user is None:
        _, response = await que_client.get_user_me(access_token=storage.get("access_token"))
    else:
        response = user
    days = response.get("days_since_created")
    text = (
        "Имя пользователя: *{username}*\n"
        "Уникальный ID: `{telegram_id}`\n\n"
        "Вы с нами {days} дней"
    ).format(
        username=response.get("username"),
        telegram_id=response.get("telegram_id"),
        days=days
    )
    profile_created = bool(response.get("profile"))
    await state.update_data({"id": response.get("id")})
    if isinstance(obj, types.Message):
        if obj.text == "<< Вернуться назад":
            await obj.answer(text="👤", reply_markup=reply.main_menu())
            await state.set_state(None)
        await obj.answer(text=text, reply_markup=inline.user_menu(is_profile=profile_created))
    elif isinstance(obj, types.CallbackQuery):
        await obj.message.edit_text(text=text, reply_markup=inline.user_menu(is_profile=profile_created))


@user_router.message(F.text, Command("reactivate"))
async def user_activate_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()
    access_token = storage.get("access_token")
    await que_client.reactivate_user(access_token=access_token)
    await message.delete()
    await message.answer(text="Поздравляем! Вы восстановили аккаунт", reply_markup=reply.main_menu())


@user_router.callback_query(F.data == "user:signout")
async def user_signout_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    text = (
        "Вы вышли из текущей сессии, чтобы войти в аккаунт используйте команду /start или кнопку ниже"
    )
    # TODO: Проверить работоспособность
    await state.clear()
    await call.message.delete()
    await call.message.answer(text=text, reply_markup=reply.login_menu())
