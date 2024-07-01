import http
from typing import (
    Any,
)

from aiogram import (
    types,
)
from aiogram.fsm.context import (
    FSMContext,
)
from aiogram.utils.i18n import (
    gettext as _,
)
from que_sdk import (
    QueClient,
    schemas,
)

from src.tgbot.config import (
    Config,
)
from src.tgbot.keyboards import (
    reply,
)
from src.tgbot.misc import (
    messages,
    security,
)


async def get_user_data(client: QueClient, storage: dict[str, Any]) -> tuple[http.HTTPStatus, dict[str, Any]]:
    access_token = storage.get("access_token")
    status_code, response = await client.get_user_me(access_token=access_token)

    return status_code, response


async def handle_send_start_message(
        message: types.Message,
        response: dict[Any, Any]
) -> None:
    username = response.get("username") if response.get("username") is not None else message.from_user.username
    await message.answer(
        text=messages.greet_auth_user.format(username=username),
        reply_markup=reply.main_menu()
    )


async def handle_login_t_me(
        client: QueClient,
        config: Config,
        message: types.Message,
        state: FSMContext,
) -> tuple[http.HTTPStatus, dict[str, Any]] | None:
    auth_data = security.generate_signature(telegram_id=message.from_user.id, secret_key=config.misc.secret_key)
    status_code, response = await client.login_t_me(data_in=schemas.TMELoginSchema(**auth_data))
    if status_code == http.HTTPStatus.OK:
        access_token, refresh_toke = response.get('access_token'), response.get('refresh_token')

        await state.update_data({"access_token": access_token, "refresh_token": refresh_toke})

    return status_code, response


async def handle_signup(
        client: QueClient,
        message: types.Message,
        state: FSMContext,
        config: Config
) -> tuple[http.HTTPStatus, dict[str, Any]]:
    username = message.from_user.username
    status_code, response = await client.signup(
        data_in=schemas.SignUpSchema(
            username=username,
            telegram_id=message.from_user.id,
        )
    )

    await message.answer(
        text=messages.welcome.format(username=username),
        reply_markup=reply.main_menu()
    )
    await handle_login_t_me(client=client, state=state, config=config, message=message)

    return status_code, response


async def handle_not_founded_user(message: types.Message) -> None:
    await message.answer(
        text=messages.not_found_user,
        reply_markup=reply.login_signup_menu()
    )


async def handle_login(
        client: QueClient,
        state: FSMContext,
        message: types.Message,
        data: dict[str, Any]
) -> tuple[http.HTTPStatus, dict[str, Any]]:
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
    return status_code, response
