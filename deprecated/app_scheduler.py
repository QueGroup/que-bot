from aiogram.types import (
    Message,
)
from loader import (
    _,
    bot,
)

from src.tgbot.keyboards.inline.questionnaires_inline import (
    viewing_ques_keyboard,
)


async def send_message_week(message: Message, db_commands=None) -> None:
    user = await db_commands.select_user(telegram_id=message.from_user.id)

    user_gender = "Парней" if user.need_partner_sex == "Мужской" else "Девушек"
    text = _(
        "Несколько {} из города {} хотят познакомиться с тобой прямо сейчас"
    ).format(user_gender, user.need_city)

    await bot.send_message(
        chat_id=message.chat.id, text=text, reply_markup=await viewing_ques_keyboard()
    )
