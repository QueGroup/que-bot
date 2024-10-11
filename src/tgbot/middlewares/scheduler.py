from typing import (
    Any,
)

from aiogram import (
    BaseMiddleware,
)
from aiogram.types import (
    TelegramObject,
)
from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,
)

from src.tgbot.types import (
    Handler,
)


class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler: AsyncIOScheduler):
        super().__init__()
        self.scheduler = scheduler

    async def __call__(
            self,
            handler: Handler,
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        data["appscheduler"] = self.scheduler
        return await handler(event, data)
