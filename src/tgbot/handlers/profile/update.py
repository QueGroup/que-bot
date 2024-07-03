from typing import (
    Any,
)

from aiogram import (
    F,
    Router,
    types,
)
from aiogram.filters import (
    StateFilter,
)
from aiogram.fsm.context import (
    FSMContext,
)
from que_sdk import (
    QueClient,
)
from que_sdk.schemas import (
    ProfileUpdateSchema,
)

from src.tgbot.keyboards import (
    inline,
    reply,
)
from src.tgbot.misc import (
    states,
)

update_profile_router = Router()


@update_profile_router.message(F.text == "✏️ Изменить")
async def update_profile_handler(message: types.Message) -> None:
    text = "Выберите, что вы хотите изменить в своём профиле"
    await message.answer(text=text, reply_markup=inline.profile_update_menu())  # type: ignore


@update_profile_router.callback_query(F.data == "first_name")
async def update_first_name_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.delete()
    await call.message.answer(text="Введите новое имя", reply_markup=reply.back_to_menu())
    await state.set_state(states.UpdateProfileSG.first_name)  # type: ignore


@update_profile_router.message(F.text, StateFilter(states.UpdateProfileSG.first_name))  # type: ignore
async def input_first_name_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()
    profile_id = storage.get("user").get("profile").get("id")
    access_token = storage.get("access_token")
    await que_client.update_profile(
        access_token=access_token,
        profile_id=profile_id,
        data_in=ProfileUpdateSchema(
            first_name=message.text
        )
    )
