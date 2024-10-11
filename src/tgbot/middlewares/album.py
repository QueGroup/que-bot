import asyncio
from typing import (
    Any,
)

from aiogram import (
    BaseMiddleware,
    types,
)

from src.tgbot.types import (
    Handler,
)


class AlbumMiddleware(BaseMiddleware):
    """
    Album middleware for capturing media groups
    """
    album_data: dict[Any, Any] = dict()

    def __init__(self, latency: int | float = 1):
        self.latency = latency
        super().__init__()

    async def __call__(
            self,
            handler: Handler,
            message: types.Message,
            data: dict[str, Any]
    ) -> None:
        if not message.media_group_id:
            await handler(message, data)
            return
        try:
            self.album_data[message.media_group_id].append(message)
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            data["_is_last"] = True
            data["album"] = self.album_data[message.media_group_id]
            await handler(message, data)

        if message.media_group_id and data.get("_is_last"):
            del self.album_data[message.media_group_id]
            del data["_is_last"]
