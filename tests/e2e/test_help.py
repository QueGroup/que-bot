from aiogram import (
    types,
)
import pytest
from telethon.tl.custom import (
    Conversation,
)


@pytest.mark.anyio
async def test_help(conv: Conversation) -> None:
    await conv.send_message("/help")
    resp: types.Message = await conv.get_response()
    assert "👍 👎" in resp.raw_text


@pytest.mark.anyio
async def test_start_handler(conv: Conversation) -> None:
    await conv.send_message('/start')
    resp: types.Message = await conv.get_response()
    resp.raw_text = resp.raw_text.replace(resp.raw_text[8:20], "")
    assert resp.raw_text == "👋 Привет вы вошли в аккаунт"
