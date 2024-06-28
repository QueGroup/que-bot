import asyncio
from concurrent.futures import (
    ThreadPoolExecutor,
)
import datetime
from decimal import (
    Decimal,
)
import http
from pathlib import (
    Path,
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
    F,
    Router,
    types,
)
from aiogram.enums import (
    ContentType,
)
from aiogram.filters import (
    StateFilter,
)
from aiogram.fsm.context import (
    FSMContext,
)
from aiogram_calendar import (
    DialogCalendar,
    DialogCalendarCallback,
    get_user_locale,
)
from que_sdk import (
    QueClient,
)
from que_sdk.schemas import (
    ProfileCreateSchema,
)
from yandex_geocoder import (
    Client,
)

from src.tgbot.filters import (
    ChatTypeFilter,
)
from src.tgbot.handlers.utils import (
    path_join,
)
from src.tgbot.keyboards import (
    inline,
    reply,
)
from src.tgbot.misc import (
    const,
    states,
)
from src.tgbot.services import (
    classification_image,
)

profile_router = Router()
profile_router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


def profile_text(profile: dict[str, Any]) -> str:
    text = (
        f"*Имя:* {profile['first_name']}\n"
        f"*Пол:* {const.genders[profile['gender']]}\n"
        f"*Дата рождения:* {profile['birthdate']}\n"
        f"*Город:* {profile['city']}\n"
        f"*О себе:* {profile['description']}\n"
        f"*Хочешь найти:* {const.interested_genders[profile['interested_in']]}\n"
        f"*Хобби:* {', '.join(profile['hobbies'])}\n"
    )
    return text


async def send_photos(folder_path: str, c: QueClient, token: str) -> None:
    for file_name in await os.listdir(folder_path):
        file_path = path_join(folder_path, file_name)
        async with aiofiles.open(file_path, "rb") as file:
            file_data = await file.read()
            status_code, response = await c.upload_photo(access_token=token, file=file_data)
            if status_code != 200:
                raise Exception(f"Failed to upload photo {file_name}: {response}")


async def delete_files_in_folder(folder_path: str) -> None:
    filenames = await aiofiles.os.listdir(folder_path)
    tasks = [aiofiles.os.remove(path_join(folder_path, filename)) for filename in filenames]
    await asyncio.gather(*tasks)


async def classify_images(user_folder: str) -> list[Any]:
    async def classify_image(file_path: str) -> bool:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, classification_image, file_path)

    filenames = await aiofiles.os.listdir(user_folder)
    tasks = [classify_image(path_join(user_folder, filename)) for filename in filenames]
    # noinspection PyTypeChecker
    return await asyncio.gather(*tasks)


async def download_photos(bot: Bot, album: list[types.Message], user_folder: str) -> None:
    tasks = []
    for i, photo in enumerate(album):
        file_id = photo.photo[-1].file_id
        file = await bot.get_file(file_id=file_id)
        file_destination = path_join(user_folder, f"photo_{file_id}.jpg")
        tasks.append(bot.download_file(file_path=file.file_path, destination=file_destination))
    await asyncio.gather(*tasks)


@profile_router.callback_query(F.data == "user:profile")
async def profile_handler(call: types.CallbackQuery, state: FSMContext, **middleware_data: Any) -> None:
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()
    # TODO: Нужно сделать кэш на время, чтобы постоянно не отправлять запросы на сервер
    _, profile = await que_client.get_profile(user_id=storage.get("id"), access_token=storage.get("access_token"))
    # await call.message.delete()
    # await call.message.answer_photo()
    await call.message.edit_text(
        text="Ваш прфиль: {profile_id}".format(profile_id=profile.get("id")), reply_markup=inline.profile_menu()
    )


@profile_router.callback_query(F.data == "user:profile-create")
@profile_router.message(F.text == "<< Вернуться назад", StateFilter(states.RegistrationSG.gender))
async def profile_create_handler(obj: types.TelegramObject, state: FSMContext) -> None:
    text = (
        "Вам нужно пройти опрос, чтобы создать профиль:\n\n"
        "Напишите мне ваше имя, которое будут все видеть в анкете"
    )
    if isinstance(obj, types.Message):
        await obj.answer(text=text, reply_markup=reply.get_user_first_name())
    if isinstance(obj, types.CallbackQuery) and state is not None:
        await obj.message.delete()
        await obj.message.answer(text=text, reply_markup=reply.get_user_first_name())
    await state.set_state(states.RegistrationSG.first_name)


@profile_router.message(F.text, StateFilter(states.RegistrationSG.first_name))
async def input_first_name_handler(
        obj: types.TelegramObject,
        state: FSMContext,
        bot: Bot
) -> None:
    text = "Принято! Выберите ваш гендер"
    first_name: str
    storage = await state.get_data()
    profile = storage.get("profile", {})
    if isinstance(obj, types.Message):
        first_name = obj.text if obj.text != "Взять из телеграмма" else obj.from_user.first_name
        profile["first_name"] = first_name
        await state.update_data({"profile": profile})
        await obj.answer(text=text, reply_markup=reply.gender_menu())

    if isinstance(obj, types.CallbackQuery):
        text = "Вы вернулись на шаг назад. Выберите ваш гендер"
        await bot.delete_message(chat_id=obj.from_user.id, message_id=obj.message.message_id - 1)
        await bot.delete_message(chat_id=obj.from_user.id, message_id=obj.message.message_id)
        await obj.message.answer(text=text, reply_markup=reply.gender_menu())
    await state.set_state(states.RegistrationSG.gender)


@profile_router.message(F.text == "♂ Мужской", StateFilter(states.RegistrationSG.gender))
@profile_router.message(F.text == "♀ Женский", StateFilter(states.RegistrationSG.gender))
@profile_router.message(F.text == "<< Вернуться назад", StateFilter(states.RegistrationSG.city))
async def input_gender_handler(message: types.Message, state: FSMContext) -> None:
    storage = await state.get_data()
    profile = storage.get("profile")

    current_year = datetime.datetime.now().year
    year = current_year - 18
    if const.genders.get(message.text):
        profile["gender"] = const.genders[message.text]
        await state.update_data({"profile": profile})
    text = (
        "Теперь выберите дату своего рождения"
    )
    await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove())
    await asyncio.sleep(0.25)
    await message.answer(
        text="Календарь:",
        reply_markup=await DialogCalendar(
            locale=await get_user_locale(message.from_user)
        ).start_calendar(year=year),
    )
    await state.set_state(states.RegistrationSG.birthday)


@profile_router.callback_query(
    DialogCalendarCallback.filter(),
    StateFilter(states.RegistrationSG.birthday)
)
@profile_router.message(F.text == "<< Вернуться назад", StateFilter(states.RegistrationSG.about_me))
async def process_dialog_calendar(
        obj: types.TelegramObject,
        state: FSMContext,
        bot: Bot,
        callback_data: DialogCalendarCallback | None = None,
) -> None:
    text = (
        "Нажмите на кнопку ниже, чтобы определить ваше местоположение! Или напишите текстом"
    )
    storage = await state.get_data()
    profile = storage.get("profile")
    if isinstance(obj, types.CallbackQuery):
        call = obj
        if callback_data.act == "CANCEL":
            await input_first_name_handler(obj=call, state=state, bot=bot)
        else:
            selected, date = await DialogCalendar(
                locale=await get_user_locale(call.from_user)
            ).process_selection(call, callback_data)
            if selected:
                current_date = datetime.datetime.now().date()
                if date.date() < current_date:
                    profile["birthdate"] = date.strftime("%Y-%m-%d")
                    await state.update_data({"profile": profile})
                    await call.message.answer(text=text, reply_markup=reply.get_location_menu())
                    await state.set_state(states.RegistrationSG.city)
                else:
                    await call.answer(text="Выбранная вами дата превышает текущую", show_alert=True)
    if isinstance(obj, types.Message):
        message = obj
        await message.answer(text=text, reply_markup=reply.get_location_menu())
        await state.set_state(states.RegistrationSG.city)


@profile_router.message(
    F.content_type.in_([ContentType.LOCATION]),
    StateFilter(states.RegistrationSG.city),
)
async def handle_user_location(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    ya_client: Client = middleware_data.get("ya_client")
    longitude = message.location.longitude
    latitude = message.location.latitude
    city = await ya_client.aioaddress(longitude=Decimal(longitude), latitude=Decimal(latitude), level="city")
    storage = await state.get_data()
    profile = storage.get("profile")
    profile.update({
        "city": city,
        "longitude": longitude,
        "latitude": latitude
    })
    await state.update_data({"profile": profile})
    text = (
        "Отлично! Теперь напишите о себе"
    )
    await message.answer(text=text, reply_markup=reply.back_to_menu())
    await state.set_state(states.RegistrationSG.about_me)


@profile_router.message(F.text != "✅ Да все хорошо!", StateFilter(states.RegistrationSG.city))
@profile_router.message(F.text == "<< Вернуться назад", StateFilter(states.RegistrationSG.interested_in))
async def input_city_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    ya_client: Client = middleware_data.get("ya_client")
    longitude, latitude = await ya_client.aiocoordinates(message.text)
    city = await ya_client.aioaddress(longitude=longitude, latitude=latitude, level="city")
    storage = await state.get_data()
    profile = storage.get("profile")
    text = (
        "Я нашел такой адрес:\n"
        "*{city}*\n"
        "Если все правильно, то подтвердите"
    ).format(city=city)
    profile.update({
        "city": city,
        "longitude": float(longitude),
        "latitude": float(latitude)
    })

    await state.update_data({"profile": profile})
    await message.answer(text=text, reply_markup=reply.confirmation_menu())


@profile_router.message(F.text == "✅ Да все хорошо!", StateFilter(states.RegistrationSG.city))
async def handle_confirmation_city(message: types.Message, state: FSMContext) -> None:
    text = (
        "Отлично! Теперь напишите о себе"
    )
    await message.answer(text=text, reply_markup=reply.back_to_menu())
    await state.set_state(states.RegistrationSG.about_me)


@profile_router.message(F.text, StateFilter(states.RegistrationSG.about_me))
@profile_router.message(F.text == "<< Вернуться назад", StateFilter(states.RegistrationSG.hobbies))
async def input_about_me_handler(message: types.Message, state: FSMContext) -> None:
    storage = await state.get_data()
    profile = storage.get("profile")
    profile["description"] = message.text
    text = "Принято! Теперь выберите кого вы бы хотели найти"

    await state.update_data({"profile": profile})
    await message.answer(text=text, reply_markup=reply.interested_in_gender_menu())
    await state.set_state(states.RegistrationSG.interested_in)


@profile_router.message(
    F.text == "♂ Парня",
    StateFilter(states.RegistrationSG.interested_in),
)
@profile_router.message(
    F.text == "♀ Девушку",
    StateFilter(states.RegistrationSG.interested_in),
)
@profile_router.message(
    F.text == "<< Вернуться назад",
    StateFilter(states.RegistrationSG.photos)
)
async def input_interested_in_handler(message: types.Message, state: FSMContext) -> None:
    gender = message.text
    storage = await state.get_data()
    profile = storage.get("profile")
    if const.interested_genders.get(gender):
        profile["interested_in"] = const.interested_genders.get(gender)
        await state.update_data({"profile": profile})
    text = (
        "Отлично! Выберите интересные для вас занятия"
    )
    await message.answer(text=text, reply_markup=reply.hobbies_menu())
    await state.set_state(states.RegistrationSG.hobbies)


@profile_router.message(F.text, StateFilter(states.RegistrationSG.hobbies))
async def input_hobbies_handler(message: types, state: FSMContext) -> None:
    storage = await state.get_data()
    selected_interests = storage.get("profile").get("hobbies", [])
    profile = storage.get("profile")
    hobby_name = message.text
    text = (
        "И напоследок, пришлите одну или несколько своих фотографий"
    )
    if hobby_name == "Подтвердить выбор":
        # FIXME:
        # if not selected_interests:
        #     await message.answer(text="Вы должны выбрать как минимум один интерес")
        # else:
        await message.answer(text=text, reply_markup=reply.get_photo_from_user_menu())
        await state.set_state(states.RegistrationSG.photos)
    elif hobby_name == "Очистить список":
        selected_interests = []
        profile["hobbies"] = selected_interests
        await state.update_data({"profile": profile})
    else:
        selected_interests.append(hobby_name)
        profile["hobbies"] = selected_interests
        await state.update_data({"profile": profile})


# TODO: WIP
@profile_router.message(
    F.text == "Взять из профиля",
    StateFilter(states.RegistrationSG.photos),
)
async def get_photo_from_user(message: types.Message, state: FSMContext, bot: Bot) -> None:
    telegram_id = message.from_user.id
    profile_pictures = await bot.get_user_profile_photos(user_id=telegram_id, limit=1)
    print(profile_pictures)


# https://ru.stackoverflow.com/questions/1456135/
# TODO: Добавить обработку одной фотографии
@profile_router.message(
    F.content_type.in_([ContentType.PHOTO]),
    StateFilter(states.RegistrationSG.photos),
)
async def user_handle_album(
        message: types.Message,
        state: FSMContext,
        bot: Bot,
        album: list[types.Message],
) -> None:
    storage = await state.get_data()
    profile = storage.get("profile")
    text = profile_text(profile)
    tg_id = message.from_user.id
    root = Path(__file__).resolve().parent.parent.parent.parent
    user_folder = rf"{root}/photos/{tg_id}/"

    if not await os.path.exists(user_folder):
        await os.mkdir(user_folder)
    if len(album) > 5:
        await message.answer(text="Превышено максимальное количество фото: не более 5")
        return

    await download_photos(bot, album, user_folder)

    is_nude = await classify_images(user_folder)

    if any(is_nude):
        await message.answer(text="Система обнаружила наготу в фотографиях. Попробуйте ещё раз")
        await delete_files_in_folder(folder_path=user_folder)
        return

    media_group = [
        types.InputMediaPhoto(media=photo.photo[-1].file_id, caption=text if i == 0 else '')
        for i, photo in enumerate(album)
    ]
    profile["folder_path"] = user_folder
    await state.update_data({"profile": profile})
    await message.answer_media_group(media=media_group)
    await message.answer(text="Подтвердите корректность данных", reply_markup=reply.confirmation_menu())
    await state.set_state(states.RegistrationSG.confirmation)


@profile_router.message(F.text == "✅ Да все хорошо!", StateFilter(states.RegistrationSG.confirmation))
async def send_profile_data_to_server(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()
    profile = storage.get("profile")
    status_code, response = await que_client.create_profile(
        data_in=ProfileCreateSchema(
            first_name=profile.get("first_name"),
            gender=profile.get("gender"),
            city=profile.get("city"),
            latitude=profile.get("latitude"),
            longitude=profile.get("longitude"),
            birthdate=profile.get("birthdate"),
            description=profile.get("description"),
            interested_in=profile.get("interested_in"),
            hobbies=profile.get("hobbies")
        ),
        access_token=storage.get("access_token")
    )
    if status_code == http.HTTPStatus.CREATED:
        await send_photos(c=que_client, token=storage.get("access_token"), folder_path=profile.get("folder_path"))
        await asyncio.sleep(0.1)
        await message.answer(text="Поздравляем, вы создали профиль", reply_markup=reply.main_menu())
    else:
        await message.answer(text="Произошла какая-то ошибка на стороне сервера. Попробуйте еще раз немного позже")
    await delete_files_in_folder(folder_path=profile.get("folder_path"))
    await state.update_data({"profile": None})
    await state.update_data({"user": None})
