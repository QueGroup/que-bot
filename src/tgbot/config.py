from dataclasses import (
    dataclass,
)
from functools import (
    lru_cache,
)
import inspect
from pathlib import (
    Path,
)

from environs import (
    Env,
)


@dataclass
class RedisConfig:
    """
    Redis configuration class.

    Attributes
    ----------
    password : Optional(str)
        The password used to authenticate with Redis.
    port : Optional(int)
        The port where Redis server is listening.
    host : Optional(str)
        The host where Redis server is located.
    """

    password: str | None
    port: int | None
    host: str | None

    def dsn(self) -> str:
        """
        Constructs and returns a Redis DSN (Data Source Name) for this database configuration.
        """
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/0"
        else:
            return f"redis://{self.host}:{self.port}/0"

    @staticmethod
    def from_env(env: Env) -> "RedisConfig":
        """
        Creates the RedisConfig object from environment variables.
        """
        password = env.str("REDIS_PASSWORD", None)
        port = env.int("REDIS_PORT")
        host = env.str("REDIS_HOST")

        return RedisConfig(password=password, port=port, host=host)


@dataclass(frozen=True, slots=True)
class TgBot:
    token: str
    admin_ids: list[int]
    support_ids: list[int]
    timezone: str
    ip: str
    moderate_chat: int
    use_redis: bool
    _BASE_DIR = Path(__file__).parent.parent.parent
    LOCALES_DIR = _BASE_DIR / "locales"

    @staticmethod
    def from_env(env: Env) -> "TgBot":
        """
        Creates the TgBot object from environment variables.
        """
        token = env.str("BOT_TOKEN")
        admin_ids = list(map(int, env.list("ADMINS")))
        support_ids = list(map(int, env.list("SUPPORTS")))
        ip = env.str("IP")
        timezone = env.str("TIMEZONE")
        moderate_chat = env.int("MODERATE_CHAT")
        use_redis = env.bool("USE_REDIS")
        return TgBot(
            token=token,
            admin_ids=admin_ids,
            support_ids=support_ids,
            ip=ip, timezone=timezone,
            moderate_chat=moderate_chat,
            use_redis=use_redis,
        )


@dataclass(frozen=True, slots=True)
class Miscellaneous:
    secret_key: str
    api_id: int | None = None
    api_hash: str | None = None
    session_str: str | None = None

    @staticmethod
    def from_env(env: Env) -> "Miscellaneous":
        """
        Creates the Miscellaneous object from environment variables.
        """
        secret_key = env.str("SIGNATURE_SECRET_KEY")
        api_id = env.int("API_ID")
        api_hash = env.str("API_HASH")
        session_str = env.str("SESSION_STR")
        return Miscellaneous(
            secret_key=secret_key,
            api_id=api_id,
            api_hash=api_hash,
            session_str=session_str
        )


@dataclass(frozen=True, slots=True)
class Config:
    tg_bot: TgBot
    misc: Miscellaneous
    redis: RedisConfig | None = None


def search_env() -> str:
    current_frame = inspect.currentframe()
    frame = current_frame.f_back
    caller_dir = Path(frame.f_code.co_filename).parent.resolve()
    start = caller_dir / ".env"
    return str(start)


def change_env(section: str, value: str) -> None:
    env = Env()
    env.read_env()

    dumped_env = env.dump()
    text = ""
    start = search_env()

    with open(start, "w", encoding="utf-8") as file:
        for v in dumped_env:
            if v:
                e = dumped_env[v]
                if v == section:
                    e = value
                text += f"{v}={e}\n"
        file.write(text)


@lru_cache
def load_config() -> Config:
    """
    This function takes an optional file path as input and returns a Config object.
    It reads environment variables from a .env file if provided, else from the process environment.
    :return: Config object with attributes set as per environment variables.
    """

    env = Env()
    env.read_env(search_env())

    return Config(
        tg_bot=TgBot.from_env(env),
        misc=Miscellaneous.from_env(env),
        redis=RedisConfig.from_env(env)
    )
