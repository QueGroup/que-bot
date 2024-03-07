# noinspection PyUnresolvedReferences
import logging
import os

import django
from aiogram import (
    executor, Dispatcher,
)

# noinspection PyUnresolvedReferences
from django_project.telegrambot.telegrambot import (
    settings,
)
from loader import (
    dp,
    scheduler,
)
from src.tgbot.filters import IsGroup, IsAdmin, IsPrivate
from src.infrastructure.db_api.db_commands import (
    reset_view_limit,
)
from src.tgbot.services.app.logger import (
    setup_logger,
)
from src.tgbot.services.app.notify_admins import (
    AdminNotification,
)
from src.tgbot.services.app.set_bot_commands import (
    set_default_commands,
)
from src.tgbot.middlewares import (
    ThrottlingMiddleware,
    LinkCheckMiddleware,
    SupportMiddleware,
    IsMaintenance,
    SchedulerMiddleware,
    BanMiddleware,
    LogMiddleware
)


def register_all_middlewares(dp: Dispatcher) -> None:
    dp.setup_middleware(ThrottlingMiddleware())
    dp.setup_middleware(LinkCheckMiddleware())
    dp.setup_middleware(SupportMiddleware())
    dp.setup_middleware(IsMaintenance())
    dp.setup_middleware(SchedulerMiddleware(scheduler))
    dp.setup_middleware(BanMiddleware())
    dp.setup_middleware(LogMiddleware())


def register_all_filters(dp: Dispatcher) -> None:
    dp.filters_factory.bind(IsGroup)
    dp.filters_factory.bind(IsPrivate)
    dp.filters_factory.bind(IsAdmin)


async def on_startup(dispatcher) -> None:
    await set_default_commands(dispatcher)
    scheduler.add_job(
        func=reset_view_limit,
        trigger="cron",
        hour=0,
        id="reset_view_limit",
        replace_existing=True,
    )
    await AdminNotification.send(dispatcher)


def setup_django():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "django_project.telegrambot.telegrambot.settings"
    )
    os.environ.update({"DJANGO_ALLOW_ASYNC_UNSAFE": "true"})
    django.setup()


if __name__ == "__main__":
    setup_django()
    setup_logger("INFO", ["aiogram.bot.api"])
    # noinspection PyUnresolvedReferences
    from src.tgbot import (
        filters,
        middlewares,
        handlers
    )

    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
