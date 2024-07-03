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
from que_sdk import (
    QueClient,
    schemas,
)

from src.tgbot.config import (
    Config,
)
from src.tgbot.misc import (
    security,
)


class AuthService:
    def __init__(self, client: QueClient, config: Config):
        self.client = client
        self.config = config

    async def get_user_data(self, storage: dict[str, Any]) -> tuple[http.HTTPStatus, dict[str, Any]]:
        access_token = storage.get("access_token")
        status_code, response = await self.client.get_user_me(access_token=access_token)

        return status_code, response

    async def handle_login_t_me(
            self,
            message: types.Message,
            state: FSMContext,
    ) -> tuple[http.HTTPStatus, dict[str, Any]] | None:
        auth_data = security.generate_signature(
            telegram_id=message.from_user.id, secret_key=self.config.misc.secret_key
        )
        status_code, response = await self.client.login_t_me(data_in=schemas.TMELoginSchema(**auth_data))
        if status_code == http.HTTPStatus.OK:
            access_token, refresh_toke = response.get('access_token'), response.get('refresh_token')

            await state.update_data({"access_token": access_token, "refresh_token": refresh_toke})

        return status_code, response
