import asyncio
from concurrent.futures import (
    ThreadPoolExecutor,
)
from typing import (
    Any,
)

import aiofiles  # type: ignore
from aiofiles import (
    os,
)
from aiogram import (
    Bot,
    types,
)
from que_sdk import (
    QueClient,
)

from src.tgbot import (
    misc,
)
from src.tgbot.services import (
    classification_image,
)


def profile_text(profile: dict[str, Any]) -> str:
    genders = {
        "male": "Мужской",
        "female": "Женский"
    }

    interested_genders = {
        "male": "Парня",
        "female": "Девушку",
    }

    if 'age' in profile:
        age = profile['age']
    elif 'birthdate' in profile:
        import datetime
        birthdate = datetime.datetime.strptime(profile['birthdate'], '%Y-%m-%d')
        age = datetime.datetime.now().year - birthdate.year
    else:
        age = 'Не указан'
    if profile["description"]:
        description = profile["description"]
    else:
        description = "Пусть"

    text = (
        f"*Имя:* {profile['first_name']}\n"
        f"*Пол:* {genders[profile['gender']]}\n"
        f"*Возраст:* {age} лет\n"
        f"*Город:* {profile['city']}\n"
        f"*О себе:* {description}\n"
        f"*Хочешь найти:* {interested_genders[profile['interested_in']]}\n"
        f"*Хобби:* {', '.join(profile['hobbies'])}\n"
    )
    return text


def public_profile_text(profile: dict[str, Any]) -> str:
    if 'age' in profile:
        age = profile['age']
    elif 'birthdate' in profile:
        import datetime
        birthdate = datetime.datetime.strptime(profile['birthdate'], '%Y-%m-%d')
        age = datetime.datetime.now().year - birthdate.year
    else:
        age = 'Не указан'

    if profile['description']:
        text = (
            f"*{profile['first_name']}*, {age} лет, {profile['city']} — "
            f"{profile['description']}\n\n"
        )
    else:
        text = (
            f"*{profile['first_name']}*, {age} лет, {profile['city']}\n"
        )
    return text


class ProfileService:

    # TODO: Убрать из параметров folder_path, а задать его прямо в __init__
    def __init__(
            self,
            folder_path: str
    ):
        self.folder_path = folder_path

    async def send_photos(self, client: QueClient, access_token: str) -> None:
        for file_name in await os.listdir(self.folder_path):
            file_path = misc.os_path_join(self.folder_path, file_name)
            async with aiofiles.open(file_path, "rb") as file:
                file_data = await file.read()
                status_code, response = await client.upload_photo(
                    access_token=access_token, file=file_data, filename=file_name,
                )
                if status_code != 200:
                    raise Exception(f"Failed to upload photo {file_name}: {response}")

    async def delete_files_in_folder(self) -> None:
        filenames = await aiofiles.os.listdir(self.folder_path)
        tasks = [aiofiles.os.remove(misc.os_path_join(self.folder_path, filename)) for filename in filenames]
        await asyncio.gather(*tasks)

    async def classify_images(self) -> list[Any]:
        async def classify_image(file_path: str) -> bool:
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor() as pool:
                return await loop.run_in_executor(pool, classification_image, file_path)

        filenames = await aiofiles.os.listdir(self.folder_path)
        tasks = [classify_image(misc.os_path_join(self.folder_path, filename)) for filename in filenames]
        # noinspection PyTypeChecker
        return await asyncio.gather(*tasks)

    async def download_photos(self, bot: Bot, photos: list[types.Message] | types.Message) -> None:
        tasks = []

        if isinstance(photos, types.Message):
            photos = [photos]

        for photo in photos:
            file_id = photo.photo[-1].file_id
            file = await bot.get_file(file_id=file_id)
            file_destination = misc.os_path_join(self.folder_path, f"photo_{file_id}.jpg")
            tasks.append(bot.download_file(file_path=file.file_path, destination=file_destination))

        await asyncio.gather(*tasks)

    async def check_photos(self) -> bool:
        is_nude = await self.classify_images()
        if any(is_nude):
            await self.delete_files_in_folder()
            return True
        return False
