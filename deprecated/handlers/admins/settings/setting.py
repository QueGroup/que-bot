from aiogram.types import (
    Message,
)

from loader import (
    dp,
)
from src.tgbot.filters.IsAdminFilter import (
    IsAdmin,
)
from src.tgbot.keyboards.admin.inline.reply_menu import (
    settings_keyboard,
)


@dp.message_handler(IsAdmin(), commands="settings", state="*")
@dp.message_handler(IsAdmin(), text="⚙️ Настройки", state="*")
async def command_start(message: Message):
    await message.answer(
        text="<u>⚙️ Настройки</u>", reply_markup=await settings_keyboard()
    )
