from typing import (
    Any,
)

from aiogram import (
    F,
    Router,
    types,
)
from aiogram.fsm.context import (
    FSMContext,
)
from que_sdk import (
    QueClient,
)

from src.tgbot import (
    services,
)
from src.tgbot.keyboards import (
    reply,
)

get_profile_router = Router()


@get_profile_router.callback_query(F.data == "user:profile")
async def profile_handler(call: types.CallbackQuery, state: FSMContext, **middleware_data: Any) -> None:
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()
    _, user = await que_client.get_user_me(access_token=storage.get("access_token"))
    profile = user.get("profile")
    photos = user.get("photos")
    text = services.profile_text(profile)
    media_group = [
        types.InputMediaPhoto(media=photo.get("remote_url"), caption=text if i == 0 else '')
        for i, photo in enumerate(photos)
    ]
    await call.message.delete()
    await call.message.answer(text="💫", reply_markup=reply.profile_menu())  # type: ignore
    await call.message.answer_media_group(
        media=media_group,
    )
