from unittest.mock import (
    AsyncMock,
)

from src.tgbot.handlers.groups.start import (
    start_group_handler,
)
import pytest

from loader import (
    _,
)


@pytest.mark.asyncio
async def test_start_group_handler() -> None:
    text_mock = _(
        "<b>Привет, я бот, проекта Que Group, для верификации анкет для знакомств</b>\n\n"
    )
    message_mock = AsyncMock(text=text_mock)
    await start_group_handler(message=message_mock)
    message_mock.answer.assert_called_with(text_mock)
