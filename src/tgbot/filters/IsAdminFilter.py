from aiogram import (
    types,
)
from aiogram.filters import BaseFilter

from src.tgbot.config import (
    load_config,
)


class IsAdmin(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id in load_config().tg_bot.admin_ids
