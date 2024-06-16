import datetime
import http
from typing import (
    Any,
)

from aiogram import (
    BaseMiddleware,
)
from aiogram.fsm.context import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
    TelegramObject,
)
from que_sdk import (
    QueClient,
)

from src.tgbot.misc.exceptions import (
    CancelHandler,
)
from src.tgbot.services import (
    welcoming_message,
)
from src.tgbot.types import (
    Handler,
)


class AccessControlMiddleware(BaseMiddleware):
    def __init__(self, client: QueClient) -> None:
        self.client = client
        self.text_deactivate = welcoming_message(message_type="deactivate_user")
        self.text_unauthorized = "Вы не вошли в аккаунт"

    async def __call__(
            self,
            handler: Handler,
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        update = data.get("event_update")
        try:
            command = update.message.text
        except AttributeError:
            command = event.data
        state = data.get("state")

        if await self._is_allowed_command(event, command):
            return await handler(event, data)

        try:
            await self._on_process_event(state=state)
            return await handler(event, data)
        except CancelHandler as e:
            await self._handle_cancel_event(event=event, e=e)

    @staticmethod
    async def _is_allowed_command(event: TelegramObject, command: str) -> bool:
        allowed_commands = {"/start", "/reactivate", "📝 Создать аккаунт", "/help"}
        if isinstance(event, CallbackQuery):
            return command in allowed_commands
        else:
            return event.web_app_data is not None or command in allowed_commands

    async def _on_process_event(self, state: FSMContext) -> None:
        storage = await state.get_data()

        if (
                storage and
                isinstance(storage.get("timestamp"), datetime.datetime) and
                datetime.datetime.now() - storage.get("timestamp") < datetime.timedelta(minutes=15)
        ):

            status_code, response = storage.get("status_code"), storage.get("response")
        else:
            status_code, response = await self.client.get_user_me(
                access_token=storage.get("access_token", "")
            )
            if status_code != http.HTTPStatus.UNAUTHORIZED or status_code == http.HTTPStatus.BAD_REQUEST:
                await state.update_data(
                    {
                        "status_code": status_code,
                        "response": response,
                        "timestamp": datetime.datetime.now()
                    }
                )
        if status_code == http.HTTPStatus.UNAUTHORIZED:
            raise CancelHandler("unauthorized")
        elif status_code == http.HTTPStatus.BAD_REQUEST:
            code = response.get("detail").get("code")
            if code == 3002:
                raise CancelHandler("deactivate")

    async def _handle_cancel_event(self, event: TelegramObject, e: CancelHandler) -> None:
        response_texts = {
            "deactivate": self.text_deactivate,
            "unauthorized": self.text_unauthorized,
        }
        response_text = response_texts.get(e.title)

        if response_text:
            await event.answer(text=response_text)
