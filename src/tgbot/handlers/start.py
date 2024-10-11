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
    StateFilter,
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
    schemas,
)

from src.tgbot.config import (
    Config,
)
from src.tgbot.filters import (
    ChatTypeFilter,
)
from src.tgbot.keyboards import (
    inline,
    reply,
)
from src.tgbot.misc import (
    messages,
)
from src.tgbot.services import (
    AuthService,
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
    auth = AuthService(client=que_client, config=config)
    if not storage:
        status_code, response = await auth.handle_login_t_me(message=message, state=state)
        if status_code == http.HTTPStatus.NOT_FOUND:
            await message.answer(
                text=messages.not_found_user,
                reply_markup=reply.login_signup_menu()
            )
    storage = await state.get_data()
    status_code, response = await auth.get_user_data(storage=storage)
    if status_code == http.HTTPStatus.BAD_REQUEST:
        code = response.get("detail").get("code")
        if code == 3002:
            await message.answer(text=messages.deactivate_user)
    else:
        if status_code != http.HTTPStatus.UNAUTHORIZED:
            username = response.get("username") if response.get("username") is not None else message.from_user.username
            await message.answer(
                text=messages.greet_auth_user.format(username=username),
                reply_markup=reply.main_menu()
            )


@start_router.message(F.text == __("📝 Создать аккаунт"))
async def signup_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    que_client: QueClient = middleware_data.get("que-client")
    config: Config = middleware_data.get("config")
    auth = AuthService(client=que_client, config=config)
    username = message.from_user.username
    status_code, response = await que_client.signup(
        data_in=schemas.SignUpSchema(
            username=username,
            telegram_id=message.from_user.id,
        )
    )

    await auth.handle_login_t_me(state=state, message=message)
    await message.answer(
        text=messages.welcome.format(username=username),
        reply_markup=reply.main_menu()
    )


@start_router.message(F.web_app_data)
async def web_app_login_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    client: QueClient = middleware_data.get("que-client")
    data = json.loads(message.web_app_data.data)
    status_code, response = await client.login(
        data_in=schemas.LoginSchema(
            username=data.get("login"),
            password=data.get("password"),
            telegram_id=message.from_user.id
        )
    )
    if status_code == http.HTTPStatus.OK:
        access_token, refresh_toke = response.get('access_token'), response.get('refresh_token')
        await state.update_data({"access_token": access_token, "refresh_token": refresh_toke})
        await message.answer(
            text=_("С возвращением, {username}").format(username=data.get("login")),
            reply_markup=reply.main_menu()
        )
    if status_code == http.HTTPStatus.UNAUTHORIZED:
        await message.answer(
            text=messages.invalid_credentials
        )


@start_router.message(F.text == __("ℹ️ О проекте"))
async def about_project_handler(message: types.Message) -> None:
    text = _(
        "Система работает на open-source"
    )
    await message.answer(text=text, reply_markup=inline.about_project_menu())


@start_router.message(F.text == "<< Вернуться назад", StateFilter(None))
async def back_to_main_reply_menu(message: types.Message) -> None:
    await message.answer(text="Вы вернулись в главное меню", reply_markup=reply.main_menu())
