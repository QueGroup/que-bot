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


class CheckActivateMiddleware(BaseMiddleware):
    def __init__(self, client: QueClient) -> None:
        self.client = client
        self.text = welcoming_message(message_type="deactivate_user")

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
        if storage and command != "/reactivate":
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
        try:
            code = response.get("detail").get("code")
            if status_code == http.HTTPStatus.BAD_REQUEST and code == 3002:
                raise CancelHandler()
        except AttributeError:
            pass
