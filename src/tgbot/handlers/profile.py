from typing import (
    Any,
)

from aiogram import (
    F,
    Router,
)
from aiogram.fsm.context import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
)
from que_sdk import (
    QueClient,
)

from src.tgbot.filters import (
    ChatTypeFilter,
)
from src.tgbot.keyboards import (
    inline,
)

profile_router = Router()
profile_router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


@profile_router.callback_query(F.data == "user:profile")
async def profile_handler(call: CallbackQuery, state: FSMContext, **middleware_data: Any) -> None:
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()
    _, profile = await que_client.get_profile(user_id=storage.get("id"), access_token=storage.get("access_token"))
    # await call.message.delete()
    # await call.message.answer_photo()
    await call.message.edit_text(
        text="Ваш профиль: {profile_id}".format(profile_id=profile.get("id")), reply_markup=inline.profile_menu()
    )


@profile_router.callback_query(F.data == "user:profile-create")
async def profile_create_handler(call: CallbackQuery, state: FSMContext, **middleware_data: Any) -> None:
    await call.message.edit_text("Вы должны заполнить анкету")
