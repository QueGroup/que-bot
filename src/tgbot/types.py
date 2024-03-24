from typing import (
    Any,
    Awaitable,
    Callable,
)

from aiogram.types import (
    Message,
)

Handler = Callable[[Message, dict[str, Any]], Awaitable[Any]]
