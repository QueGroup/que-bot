import asyncio

from aiogram.types import (
    CallbackQuery,
)

from loader import (
    _,
    bot,
    dp,
)
from src.tgbot.config import (
    load_config,
)
from src.tgbot.filters.IsAdminFilter import (
    IsAdmin,
)
from src.infrastructure.db_api import (
    db_commands,
)
from src.tgbot.keyboards.inline.main_menu_inline import (
    start_keyboard,
)
from src.tgbot.keyboards.inline.poster_inline import (
    poster_keyboard,
)


# FIXME: Broken handler
@dp.callback_query_handler(
    IsAdmin(),
    lambda call: str(call.message.chat.id) == load_config().tg_bot.moderate_chat,
)
async def order_answer(call: CallbackQuery) -> None:
    call_data = call.data.split("-")
    telegram_id = call_data[1]
    markup = await start_keyboard(obj=int(telegram_id))
    if call_data[0] == "moderate_accept":
        await call.message.delete()
        await call.message.answer(_("Принято!"))
        await db_commands.update_user_meetings_data(
            telegram_id=telegram_id,
            verification_status=True,
            is_admin=True,
            moderation_process=False,
        )
        await bot.send_message(
            chat_id=telegram_id,
            text=_("Ваше мероприятие прошло модерацию"),
            reply_markup=markup,
        )
        await asyncio.sleep(1)

    elif call_data[0] == "moderate_decline":
        await call.message.delete()
        await call.message.answer(_("Отклонено!"))
        await db_commands.delete_user_meetings(telegram_id=telegram_id)
        await bot.send_message(
            chat_id=telegram_id,
            text=_("К сожалению ваше мероприятие не прошло модерацию"),
            reply_markup=await poster_keyboard(obj=call),
        )
    await db_commands.update_user_meetings_data(
        telegram_id=telegram_id, moderation_process=False
    )
