import inspect
from dataclasses import (
    dataclass,
)
from functools import (
    lru_cache,
)
from pathlib import (
    Path,
)

from environs import (
    Env,
)
from yarl import (
    URL,
)


@dataclass(frozen=True, slots=True)
class DataBaseConfig:
    """
    Database configuration class.
    This class holds the settings for the database, such as host, password, port, etc.

    Attributes
    ----------
    host : str
        The host where the database server is located.
    password : str
        The password used to authenticate with the database.
    user : str
        The username used to authenticate with the database.
    database : str
        The name of the database.
    port : int
        The port where the database server is listening.
    """
    user: str
    password: str
    host: str
    database: str
    port: str

    @staticmethod
    def from_env(env: Env):
        """
        Creates the DbConfig object from environment variables.
        """
        host = env.str("DB_HOST")
        password = env.str("POSTGRES_PASSWORD")
        user = env.str("POSTGRES_USER")
        database = env.str("POSTGRES_DB")
        port = env.int("DB_PORT", 5432)
        return DataBaseConfig(
            host=host, password=password, user=user, database=database, port=port
        )


@dataclass
class RedisConfig:
    """
    Redis configuration class.

    Attributes
    ----------
    redis_pass : Optional(str)
        The password used to authenticate with Redis.
    redis_port : Optional(int)
        The port where Redis server is listening.
    redis_host : Optional(str)
        The host where Redis server is located.
    """

    redis_pass: str | None
    redis_port: int | None
    redis_host: str | None

    def dsn(self) -> str:
        """
        Constructs and returns a Redis DSN (Data Source Name) for this database configuration.
        """
        if self.redis_pass:
            return f"redis://:{self.redis_pass}@{self.redis_host}:{self.redis_port}/0"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def from_env(env: Env):
        """
        Creates the RedisConfig object from environment variables.
        """
        redis_pass = env.str("REDIS_PASSWORD")
        redis_port = env.int("REDIS_PORT")
        redis_host = env.str("REDIS_HOST")

        return RedisConfig(redis_pass=redis_pass, redis_port=redis_port, redis_host=redis_host)


@dataclass(frozen=True, slots=True)
class TgBot:
    token: str
    admin_ids: list[int]
    support_ids: list[int]
    timezone: str
    ip: str
    I18N_DOMAIN: str
    moderate_chat: int
    use_redis: bool

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
        I18N_DOMAIN = "dating"
        moderate_chat = env.int("MODERATE_CHAT")
        use_redis = env.bool("USE_REDIS")
        return TgBot(
            token=token,
            admin_ids=admin_ids,
            support_ids=support_ids,
            ip=ip, timezone=timezone,
            moderate_chat=moderate_chat,
            I18N_DOMAIN=I18N_DOMAIN,
            use_redis=use_redis,
        )


@dataclass(frozen=True, slots=True)
class Miscellaneous:
    secret_key: str
    yandex_api_key: str
    client_id: str
    redirect_url: URL
    yoomoney_key: str
    production: bool

    @staticmethod
    def from_env(env: Env) -> "Miscellaneous":
        """
        Creates the Miscellaneous object from environment variables.
        """
        secret_key = env.str("SECRET_KEY")
        yandex_api_key = env.str("API_KEY")
        client_id = env.str("CLIENT_ID")
        redirect_url = env.str("REDIRECT_URI")
        yoomoney_key = env.str("YOOMONEY_KEY")
        production = env.bool("PRODUCTION")
        return Miscellaneous(
            secret_key=secret_key,
            yandex_api_key=yandex_api_key,
            client_id=client_id,
            redirect_url=redirect_url,
            production=production,
            yoomoney_key=yoomoney_key
        )


@dataclass(frozen=True, slots=True)
class Config:
    tg_bot: TgBot
    db: DataBaseConfig
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
        db=DataBaseConfig.from_env(env),
        misc=Miscellaneous.from_env(env),
    )
