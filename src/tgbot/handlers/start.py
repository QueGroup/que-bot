import http
import json
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
from aiogram.utils.i18n import (
    gettext as _,
    lazy_gettext as __,
)
from que_sdk import (
    QueClient,
)

from src.tgbot import (
    services,
)
from src.tgbot.config import (
    Config,
)
from src.tgbot.filters import (
    ChatTypeFilter,
)
from src.tgbot.keyboards import (
    inline,
)

start_router = Router()
start_router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


@start_router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    config: Config = middleware_data.get("config")
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()
    if not storage:
        status_code, response = await services.handle_login_t_me(que_client, config, message, state)
        if status_code == http.HTTPStatus.NOT_FOUND:
            await services.handle_not_founded_user(message=message)
    storage = await state.get_data()
    status_code, response = await services.get_user_data(que_client, storage)
    if status_code == http.HTTPStatus.BAD_REQUEST:
        code = response.get("detail").get("code")
        if code == 3002:
            await message.answer(text=services.welcoming_message(message_type="deactivate_user"))
    else:
        if status_code != http.HTTPStatus.UNAUTHORIZED:
            await services.handle_send_start_message(message=message, response=response)


@start_router.message(F.text == __("📝 Создать аккаунт"))
async def signup_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    client: QueClient = middleware_data.get("que-client")
    config: Config = middleware_data.get("config")
    await services.handle_signup(client=client, message=message, state=state, config=config)


@start_router.message(F.web_app_data)
async def web_app_login_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    client: QueClient = middleware_data.get("que-client")
    data = json.loads(message.web_app_data.data)
    await services.handle_login(client=client, message=message, state=state, data=data)


@start_router.message(F.text == __("ℹ️ О проекте"))
async def about_project_handler(message: types.Message) -> None:
    text = _(
        "Система работает на open-source"
    )
    await message.answer(text=text, reply_markup=inline.about_project_menu())
