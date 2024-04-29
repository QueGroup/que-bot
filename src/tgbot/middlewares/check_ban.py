from typing import (
    Any,
)

from aiogram import (
    BaseMiddleware,
)
from aiogram.types import (
    TelegramObject,
)

from src.tgbot.types import (
    Handler,
)


class BanMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Handler,
            event: TelegramObject,
            data: dict[str, Any]
    ) -> Any:
        pass

    # @staticmethod
    # async def is_banned(user):
    #     try:
    #         return user.is_banned
    #     except AttributeError:
    #         return False

    # async def on_process_message(self, message: types.Message, data: dict) -> None:
    #     await self.check_ban_user(obj=message)
    #
    # async def on_process_callback_query(
    #         self, call: types.CallbackQuery, data: dict
    # ) -> None:
    #     user = await db_commands.select_user(telegram_id=call.from_user.id)
    #     if (user is not None and await self.is_banned(user=user)) and (
    #             call.data != "unban"
    #             and call.data != "unban_menu"
    #             and call.data != "Yoomoney:check_payment"
    #             and call.data != "cancel_payment"
    #             and call.data != "Yoomoney"
    #     ):
    #         await self.check_ban_user(obj=call)
    #
    # async def check_ban_user(
    #         self, obj: types.CallbackQuery | types.Message
    # ) -> NoReturn:
    #     user = await db_commands.select_user(telegram_id=obj.from_user.id)
    #
    #     text = _("😢 Вы заблокированы!")
    #     markup = await unban_user_keyboard()
    #     if await self.is_banned(user=user):
    #         try:
    #             await obj.answer(text=text, reply_markup=markup)
    #         except TypeError:
    #             await obj.message.answer(text=text, reply_markup=markup)
    #         raise CancelHandler()
