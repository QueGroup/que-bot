from typing import (
    Any,
)

from aiogram import (
    types,
)
from aiogram.utils.i18n import (
    I18nMiddleware,
)

from src.tgbot.config import (
    LOCALES_DIR,
    load_config,
)


async def get_lang(user_id, db_commands=None) -> str | None:
    user = await db_commands.select_user(telegram_id=user_id)
    return user.language if user else None


class ACLMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: tuple[Any]) -> str | None:
        user_id = types.User.get_current().id
        return await get_lang(user_id) or (await super().get_user_locale(action, args))


def setup_middleware(dp) -> ACLMiddleware:
    i18n = ACLMiddleware(load_config().tg_bot.I18N_DOMAIN, LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n
