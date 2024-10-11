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
from yandex_geocoder import (
    Client,
)

from src.tgbot.config import (
    Config,
)
from src.tgbot.types import (
    Handler,
)


class DIMiddleware(BaseMiddleware):
    def __init__(
            self,
            config: Config,
            client: QueClient,
            ya_client: Client
    ) -> None:
        self.config = config
        self.client = client
        self.ya_client = ya_client

    async def __call__(
            self,
            handler: Handler,
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        data["config"] = self.config
        data["que-client"] = self.client
        data["ya_client"] = self.ya_client

        return await handler(event, data)
