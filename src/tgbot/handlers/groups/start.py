from aiogram.dispatcher.filters import (
    Command,
)
from aiogram.types import (
    Message,
)

from loader import (
    _,
    dp,
)
from src.tgbot.filters.FiltersChat import (
    IsGroup,
)
from src.tgbot.filters.IsAdminFilter import (
    IsAdmin,
)


@dp.message_handler(IsGroup(), IsAdmin(), Command("start"))
async def start_group_handler(message: Message) -> None:
    await message.answer(
        text=_(
            "<b>Привет, я бот, проекта Que Group, для верификации анкет для знакомств</b>\n\n"
        )
    )
