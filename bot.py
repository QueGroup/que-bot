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
from aiogram.utils.i18n import (
    ConstI18nMiddleware,
    I18n,
)
import betterlogging as bl
from que_sdk import (
    QueClient,
)
from redis.asyncio.client import Redis  # type: ignore
from yandex_geocoder import (
    Client,
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
from src.tgbot.middlewares import (  # ThrottlingMiddleware,
    AccessControlMiddleware,
    AlbumMiddleware,
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
        client: QueClient,
        redis: Redis,
        i18n: I18n,
        ya_client: Client
) -> None:
    logging.info("Setup middlewares...")
    middleware_types = [
        MiscMiddleware(config, client, ya_client),
        AccessControlMiddleware(client=client),
        ConstI18nMiddleware(locale="ru", i18n=i18n)
    ]
    # dp.message.middleware(ThrottlingMiddleware(redis))
    dp.message.middleware(AlbumMiddleware())
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
    i18n = I18n(path=config.tg_bot.LOCALES_DIR, default_locale="ru", domain="messages")
    storage = get_storage(config)
    client = QueClient()
    ya_client = Client(api_key=config.misc.yandex_map_api_key) # type: ignore

    redis = Redis(
        host=config.redis.host,
        port=config.redis.port,
        decode_responses=True,
        max_connections=10,
        auto_close_connection_pool=True
    )

    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher(storage=storage)

    register_global_middlewares(dp, config, client, redis, i18n, ya_client)
    dp.include_routers(*routers_list)
    await services.set_default_commands(bot, config)
    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        # FIXME: Почему-то с редисом asyncio.run(main()) не работает
        asyncio.get_event_loop().run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот был выключен!")
