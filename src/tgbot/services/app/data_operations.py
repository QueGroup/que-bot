import shutil

import aiofiles

from src.infrastructure.db_api import (
    db_commands,
)


async def dump_users_to_file():
    async with aiofiles.open("users.txt", "w", encoding="utf-8") as file:
        _text = ""
        _users = await db_commands.select_all_users()
        for user in _users:
            _text += str(user) + "\n"

        await file.write(_text)

    return "users.txt"


async def backup_configs():
    shutil.make_archive("backup_data", "zip", "./logs/")
    return "./backup_data.zip"
