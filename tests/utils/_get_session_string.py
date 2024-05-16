from telethon import (
    TelegramClient,
)
from telethon.sessions import (
    StringSession,
)

api_id = 28394664
api_hash = "59e0397dd64ba527b2761ed10f4d92de"

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("Session string:", client.session.save())
