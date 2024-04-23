from typing import (
    Literal,
)

from aiogram import (
    types,
)
from aiogram.fsm.context import (
    FSMContext,
)
from que_sdk import (
    QueClient,
    SignUpSchema,
    TMELoginSchema,
)

from src.tgbot.config import (
    Config,
)
from src.tgbot.keyboards import (
    reply,
)
from src.tgbot.misc import (
    security,
)


def welcoming_message(username: str, message_type: Literal["welcome", "greet_auth_user"]) -> str:
    messages = {
        "welcome": "Добро пожаловать, {username}! Вы создали новый аккаунт".format(username=username),
        "greet_auth_user": "Привет {username} вы вошли в аккаунт".format(username=username)
    }

    return messages[message_type]


async def get_user_data(client: QueClient, storage: dict):
    access_token = storage.get("access_token")
    status_code, response = await client.get_user_me(access_token)

    return status_code, response


async def handle_send_start_message(username: str, message: types.Message):
    await message.answer(
        text=welcoming_message(username=username, message_type="greet_auth_user"),
        reply_markup=reply.main_menu()
    )


async def handle_login_t_me(client: QueClient, config: Config, message: types.Message, state: FSMContext):
    auth_data = security.generate_signature(telegram_id=message.from_user.id, secret_key=config.misc.secret_key)
    status_code, response = await client.login_t_me(data_in=TMELoginSchema(**auth_data))
    access_token, refresh_toke = response.get('access_token'), response.get('refresh_token')

    await state.update_data({"access_token": access_token, "refresh_token": refresh_toke})

    return status_code, response


async def handle_signup(client: QueClient, message: types.Message, state: FSMContext, config: Config):
    username = message.from_user.username
    status_code, response = await client.signup(
        data_in=SignUpSchema(
            username=username,
            telegram_id=message.from_user.id,
        )
    )

    await message.answer(
        text=welcoming_message(username=username, message_type="welcome"),
        reply_markup=reply.main_menu()
    )
    await handle_login_t_me(client=client, state=state, config=config, message=message)

    return status_code, response


async def handle_not_founded_user(message: types.Message):
    await message.answer(
        text="Мы не смогли найти ваш в аккаунт. Создайте новый или войдите с помощью логина и пароля",
        reply_markup=reply.login_signup_menu()
    )
