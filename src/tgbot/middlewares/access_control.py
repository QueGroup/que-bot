import http
from typing import (
    Any,
)

from aiogram import (
    BaseMiddleware,
)
from aiogram.types import (
    TelegramObject,
)
from que_sdk import (
    QueClient,
)

from src.tgbot.services import (
    welcoming_message,
)
from src.tgbot.types import (
    Handler,
)

from .exceptions import (
    CancelHandler,
)


# TODO: Проверить ещё забанен ли пользователь или нет
class AccessControlMiddleware(BaseMiddleware):
    def __init__(self, client: QueClient) -> None:
        self.client = client
        self.text_deactivate = welcoming_message(message_type="deactivate_user")
        self.text_unauthorized = "Вы не вошли в аккаунт"

    # FIXME: REFACTOR ME
    async def __call__(  # type: ignore
            self,
            handler: Handler,
            event: TelegramObject,
            data: dict[str, Any]
    ) -> Handler | None:
        update = data.get("event_update")
        try:
            command = update.message.text
        except AttributeError:
            command = event.data
        state = data.get("state")
        storage = await state.get_data()

        try:
            if (
                    event.web_app_data is not None or
                    command == "/start" or
                    command == "/reactivate" or
                    command == "📝 Создать аккаунт"
            ):
                return await handler(event, data)
        except AttributeError:
            return await handler(event, data)

        try:
            await self.on_process_event(storage=storage)
            return await handler(event, data)
        except CancelHandler as e:
            if e.title == "deactivate":
                await event.answer(text=self.text_deactivate)
            else:
                await event.answer(text=self.text_unauthorized)

    async def on_process_event(self, storage: dict[str, Any]) -> None:
        status_code, response = await self.client.get_user_me(
            access_token=storage.get("access_token", "")
        )
        if status_code == http.HTTPStatus.UNAUTHORIZED:
            raise CancelHandler("unauthorized")
        elif status_code == http.HTTPStatus.BAD_REQUEST:
            code = response.get("detail").get("code")
            if code == 3002:
                raise CancelHandler("deactivate")
