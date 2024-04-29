import http
from typing import (
    Any,
)

from aiogram import (
    F,
    Router,
    types,
)
from aiogram.filters import (
    CommandStart,
)
from aiogram.fsm.context import (
    FSMContext,
)
from que_sdk import (
    QueClient,
)

from src.tgbot.config import (
    Config,
)
from src.tgbot.keyboards import (
    inline,
)
from src.tgbot.services import (
    get_user_data,
    handle_login_t_me,
    handle_not_founded_user,
    handle_signup,
    welcoming_message,
)
from src.tgbot.services.app import (
    handle_send_start_message,
)

start_router = Router()


@start_router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    config: Config = middleware_data.get("config")
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()

    if not storage:
        status_code, response = await handle_login_t_me(que_client, config, message, state)
        if status_code == http.HTTPStatus.NOT_FOUND:
            await handle_not_founded_user(message=message)
    storage = await state.get_data()
    status_code, response = await get_user_data(que_client, storage)
    if status_code == http.HTTPStatus.BAD_REQUEST:
        code = response.get("detail").get("code")
        if code == 3002:
            await message.answer(text=welcoming_message(message_type="deactivate_user"))
    else:
        if status_code != http.HTTPStatus.UNAUTHORIZED:
            await handle_send_start_message(message=message, response=response)


@start_router.message(F.text == "✏️ Создать аккаунт")
async def signup_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    client: QueClient = middleware_data.get("que-client")
    config: Config = middleware_data.get("config")
    await handle_signup(client=client, message=message, state=state, config=config)


@start_router.message(F.text == "❔ О проекте")
async def about_project_handler(message: types.Message) -> None:
    text = (
        "Наша система полностью open-source"
    )
    await message.answer(text=text, reply_markup=inline.about_project_menu())
