import logging
from typing import (
    Any,
)

from aiogram import (
    Bot,
    Dispatcher,
    types,
)
from aiogram.contrib.fsm_storage.memory import (
    MemoryStorage,
)
from aiogram.contrib.fsm_storage.redis import (
    RedisStorage2,
)
from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,
)
from nudenet import (
    NudeDetector,
)

from src.tgbot.config import load_config
from src.infrastructure.YandexMap.api import (
    Client,
)
from src.infrastructure.yoomoney import (
    YooMoneyWallet,
)
from src.tgbot.services.app.language_ware import setup_middleware

bot = Bot(token=load_config().tg_bot.token, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2() if load_config().tg_bot.use_redis else MemoryStorage()
dp = Dispatcher(bot, storage=storage)
client = Client(api_key=load_config().misc.yandex_api_key)
job_defaults = dict(coalesce=False, max_instances=3)
scheduler = AsyncIOScheduler(
    timezone=load_config().tg_bot.timezone, job_defaults=job_defaults
)
wallet = YooMoneyWallet(access_token=load_config().misc.yoomoney_key)
detector = NudeDetector()

i18n = setup_middleware(dp)
_: Any = i18n.gettext

logger = logging.getLogger(__name__)
