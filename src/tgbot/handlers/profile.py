import asyncio
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

from aiofiles import (  # type: ignore
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

from src.tgbot import (
    services,
)
from src.tgbot.filters import (
    ChatTypeFilter,
)
from src.tgbot.keyboards import (
    inline,
    reply,
)
from src.tgbot.misc import (
    states,
)

profile_router = Router()
profile_router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


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
    reply_markup = reply.get_user_first_name()
    if isinstance(obj, types.Message):
        await obj.answer(text=text, reply_markup=reply_markup)
    if isinstance(obj, types.CallbackQuery) and state is not None:
        await obj.message.delete()
        await obj.message.answer(text=text, reply_markup=reply_markup)
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
    genders = {
        "♂ Мужской": "male",
        "♀ Женский": "female"
    }
    current_year = datetime.datetime.now().year
    year = current_year - 18
    if genders.get(message.text):
        profile["gender"] = genders[message.text]
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
    interested_genders = {
        "♂ Парня": "male",
        "♀ Девушку": "female",
    }
    profile = storage.get("profile")
    if interested_genders.get(gender):
        profile["interested_in"] = interested_genders.get(gender)
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
        if not selected_interests:
            await message.answer(text="Вы должны выбрать как минимум один интерес")
        else:
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


# https://ru.stackoverflow.com/questions/1456135/
@profile_router.message(
    F.content_type.in_([ContentType.PHOTO]),
    StateFilter(states.RegistrationSG.photos),
)
async def user_handle_album(
        message: types.Message,
        state: FSMContext,
        bot: Bot,
        album: list[types.Message] | None = None,
) -> None:
    storage = await state.get_data()
    profile = storage.get("profile")
    text = services.profile_text(profile)
    telegram_id = message.from_user.id
    root = Path(__file__).resolve().parent.parent.parent.parent
    user_folder = rf"{root}/photos/{telegram_id}/"
    profile_service = services.ProfileService(user_folder)
    censor_warning_text = "Система обнаружила наготу в фотографиях. Попробуйте ещё раз"

    if not await os.path.exists(user_folder):
        await os.mkdir(user_folder)

    if album is None:
        await profile_service.download_photos(bot=bot, photos=message)

        if await profile_service.check_photos():
            await message.answer(text=censor_warning_text)

        file_id = message.photo[-1].file_id
        await message.answer_photo(photo=file_id, caption=text)
    else:
        if len(album) > 5:
            await message.answer(text="Превышено максимальное количество фото: не более 5")
            return

        await profile_service.download_photos(bot=bot, photos=album)
        if await profile_service.check_photos():
            await message.answer(text=censor_warning_text)

        media_group = [
            types.InputMediaPhoto(media=photo.photo[-1].file_id, caption=text if i == 0 else '')
            for i, photo in enumerate(album)
        ]
        await message.answer_media_group(media=media_group)
    profile["folder_path"] = user_folder
    await state.update_data({"profile": profile})
    await state.update_data({"profile_service": profile_service})
    await message.answer(text="Подтвердите корректность данных", reply_markup=reply.confirmation_menu())
    await state.set_state(states.RegistrationSG.confirmation)


@profile_router.message(F.text == "✅ Да все хорошо!", StateFilter(states.RegistrationSG.confirmation))
async def send_profile_data_to_server(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()
    profile = storage.get("profile")
    profile_service: services.ProfileService = storage.get("profile_service")
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
        await profile_service.send_photos(client=que_client, access_token=storage.get("access_token"))
        await message.answer(text="Поздравляем, вы создали профиль", reply_markup=reply.main_menu())
    else:
        await message.answer(text="Произошла какая-то ошибка на стороне сервера. Попробуйте еще раз немного позже")
    await profile_service.delete_files_in_folder()
    await state.update_data({"profile": None})
    await state.update_data({"user": None})
