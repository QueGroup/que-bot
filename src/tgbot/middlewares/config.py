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

from src.tgbot.config import (
    Config,
)
from src.tgbot.types import (
    Handler,
)


class MiscMiddleware(BaseMiddleware):
    def __init__(self, config: Config, client: QueClient) -> None:
        self.config = config
        self.client = client

    async def __call__(
            self,
            handler: Handler,
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        data["config"] = self.config
        data["que-client"] = self.client
        return await handler(event, data)
