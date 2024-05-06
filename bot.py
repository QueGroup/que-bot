import asyncio
import logging
from typing import (
    Sequence,
)

from aiogram import (
    Bot,
    Dispatcher,
)
from aiogram.client.default import (
    DefaultBotProperties,
)
from aiogram.enums import (
    ParseMode,
)
from aiogram.fsm.storage.memory import (
    MemoryStorage,
)
from aiogram.fsm.storage.redis import (
    DefaultKeyBuilder,
    RedisStorage,
)
import betterlogging as bl
from que_sdk import (
    QueClient,
)

from src.tgbot import (
    services,
)
from src.tgbot.config import (
    Config,
    load_config,
)
from src.tgbot.handlers import (
    routers_list,
)
from src.tgbot.middlewares import (
    AccessControlMiddleware,
    MiscMiddleware,
)


async def on_startup(bot: Bot, admin_ids: Sequence[int]) -> None:
    await services.broadcaster.broadcast(bot, list(admin_ids), "Бот запущен")


def setup_logging() -> None:
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.

    Returns:
        None

    Example usage:
        setup_logging()
    """
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def register_global_middlewares(
        dp: Dispatcher,
        config: Config,
        client: QueClient
) -> None:
    logging.info("Setup middlewares...")
    middleware_types = [
        MiscMiddleware(config, client),
        AccessControlMiddleware(client=client)
    ]
    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def get_storage(config: Config) -> MemoryStorage | RedisStorage:
    """
    Return storage based on the provided configuration.

    Args:
        config (Config): The configuration object.

    Returns:
        Storage: The storage object based on the configuration.
    """
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def main() -> None:
    setup_logging()

    config = load_config()
    storage = get_storage(config)
    client = QueClient()
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher(storage=storage)

    dp.include_routers(*routers_list)

    register_global_middlewares(dp, config, client)

    await services.set_default_commands(bot, config)
    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот был выключен!")
