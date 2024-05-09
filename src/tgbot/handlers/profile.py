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
    # que_client: QueClient = middleware_data.get("que-client")
    # storage = await state.get_data()
    # await call.message.delete()
    # await call.message.answer_photo()
    await call.message.edit_text(text="Ваш профиль: ", reply_markup=inline.profile_menu())
