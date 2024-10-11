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

from src.tgbot.misc import (
    states,
)

delete_router = Router()


@delete_router.message(F.text == "🗑 Удалить")
async def delete_profile_handler(message: types.Message, state: FSMContext) -> None:
    storage = await state.get_data()
    username = storage.get("user").get("username")
    await message.answer(
        text=f"Вы точно хотите удалить свой профиль? Чтобы подтвердить свое действие напишите свой username: `{username}`"
    )
    await state.set_state(states.DeleteProfileSG.confirmation)


@delete_router.message(F.text, StateFilter(states.DeleteProfileSG.confirmation))
async def confirmation_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()
    username = storage.get("user").get("username")
    profile_id = storage.get("user").get("profile").get("id")
    access_token = storage.get("access_token")
    if message.text == username:
        # FIXME: Выбрасывается JSONDecodeError,
        #  скорее всего из-за того, что никакой json не возвращается, хотя внутри мы там обрабатываем response.json
        await que_client.delete_profile(profile_id=profile_id, access_token=access_token)
        await state.set_state(None)
    else:
        await message.answer(text="Вы неправильно ввели свой username. Попробуйте еще раз")
        return
