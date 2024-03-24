from typing import (
    Any,
    Dict,
)

from aiogram import (
    BaseMiddleware,
)
from aiogram.types import (
    Message,
)

from src.tgbot.types import (
    Handler,
)


class ConfigMiddleware(BaseMiddleware):
    def __init__(self, config) -> None:
        self.config = config

    async def __call__(
            self,
            handler: Handler,
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        data["config"] = self.config
        return await handler(event, data)
