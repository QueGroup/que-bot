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

from src.tgbot.types import (
    Handler,
)

from .exceptions import (
    CancelHandler,
)


class IsAuthMiddleware(BaseMiddleware):
    def __init__(self, client: QueClient) -> None:
        self.client = client
        self.text = (
            "Вы не вошли в аккаунт"
        )

    async def __call__(
            self,
            handler: Handler,
            event: TelegramObject,
            data: dict[str, Any]
    ) -> Any:
        update = data.get("event_update")
        command = update.message.text
        state = data.get("state")
        storage = await state.get_data()

        if command != "/start":
            try:
                await self.on_process_event(storage=storage)
                return await handler(event, data)
            except CancelHandler:
                await event.answer(text=self.text)
        else:
            return await handler(event, data)

    async def on_process_event(self, storage: dict[str, Any]) -> Any:
        status_code, response = await self.client.get_user_me(
            access_token=storage.get("access_token", "")
        )
        if status_code == http.HTTPStatus.UNAUTHORIZED:
            raise CancelHandler()
