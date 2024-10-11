from decimal import (
    Decimal,
)
from typing import (
    Any,
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
from que_sdk import (
    QueClient,
)
from que_sdk.schemas import (
    ProfileUpdateSchema,
)
from yandex_geocoder import (
    Client,
)

from src.tgbot.keyboards import (
    inline,
    reply,
)
from src.tgbot.misc import (
    messages,
    states,
)

update_router = Router()


async def delete_message_and_reply(
        call: types.CallbackQuery, text: str, reply_markup: types.ReplyKeyboardMarkup
) -> None:
    await call.message.delete()
    await call.message.answer(text=text, reply_markup=reply_markup)


async def update_profile_and_send_menu(
        state: FSMContext, fields: dict[str, Any], middleware_data: Any, message: types.Message
) -> None:
    await update_profile_field(state=state, fields=fields, middleware_data=middleware_data)
    await update_profile_handler(message=message)


async def update_profile_field(state: FSMContext, fields: dict[str, Any], middleware_data: dict[str, Any]) -> None:
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()
    profile_id = storage.get("user").get("profile").get("id")
    access_token = storage.get("access_token")
    await que_client.update_profile(
        access_token=access_token,
        profile_id=profile_id,
        data_in=ProfileUpdateSchema(**fields)
    )


@update_router.message(F.text == "✏️ Изменить")
async def update_profile_handler(message: types.Message, bot: Bot) -> None:
    await message.answer(text="ㅤ", reply_markup=types.ReplyKeyboardRemove())
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id + 1)
    await message.answer(text=messages.update_profile, reply_markup=inline.profile_update_menu())


@update_router.callback_query(F.data == "first_name")
async def update_first_name_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    await delete_message_and_reply(call=call, text="Введите новое имя", reply_markup=reply.back_to_menu())
    await state.set_state(states.UpdateProfileSG.first_name)


@update_router.message(F.text, StateFilter(states.UpdateProfileSG.first_name))
async def input_first_name_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    await update_profile_and_send_menu(
        state=state, message=message, middleware_data=middleware_data, fields={"first_name": message.text}
    )
    await state.set_state(None)


@update_router.callback_query(F.data == "gender")
async def update_gender_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    await delete_message_and_reply(call=call, text="Выберите новый пол", reply_markup=reply.gender_menu())
    await state.set_state(states.UpdateProfileSG.gender)


@update_router.message(F.text, StateFilter(states.UpdateProfileSG.gender))
async def input_gender_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    genders = {
        "♂ Мужской": "male",
        "♀ Женский": "female"
    }
    gender = genders.get(message.text)
    if gender:
        await update_profile_and_send_menu(
            state=state, message=message, middleware_data=middleware_data, fields={"gender": gender}
        )
        await state.set_state(None)
    else:
        await message.answer("Попробуйте ещё раз")
        return


@update_router.callback_query(F.data == "city")
async def update_city_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    await delete_message_and_reply(
        call=call,
        text="Нажмите на кнопку ниже, чтобы определить ваше местоположение! Или напишите текстом",
        reply_markup=reply.get_location_menu()
    )
    await state.set_state(states.UpdateProfileSG.city)


@update_router.message(F.text != "✅ Да все хорошо!", StateFilter(states.UpdateProfileSG.city))
async def input_city_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    ya_client: Client = middleware_data.get("ya_client")
    longitude, latitude = await ya_client.aiocoordinates(message.text)
    city = await ya_client.aioaddress(longitude=longitude, latitude=latitude, level="city")
    text = (
        "Я нашел такой адрес:\n"
        "*{city}*\n"
        "Если все правильно, то подтвердите"
    ).format(city=city)
    await state.update_data({
        "city": city,
        "longitude": float(longitude),
        "latitude": float(latitude)
    })
    await message.answer(text=text, reply_markup=reply.confirmation_menu())


@update_router.message(F.text == "✅ Да все хорошо!", StateFilter(states.UpdateProfileSG.city))
async def save_city_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    storage = await state.get_data()
    fields = {
        "city": storage.get("city"),
        "longitude": storage.get("longitude"),
        "latitude": storage.get("latitude")
    }
    await update_profile_and_send_menu(
        state=state, message=message, middleware_data=middleware_data, fields=fields
    )
    await state.set_state(None)


@update_router.message(
    F.content_type.in_([ContentType.LOCATION]),
    StateFilter(states.UpdateProfileSG.city),
)
async def determine_city_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    ya_client: Client = middleware_data.get("ya_client")
    longitude = message.location.longitude
    latitude = message.location.latitude
    city = await ya_client.aioaddress(longitude=Decimal(longitude), latitude=Decimal(latitude), level="city")
    fields = {
        "city": city,
        "longitude": longitude,
        "latitude": latitude
    }
    await update_profile_and_send_menu(
        state=state, message=message, middleware_data=middleware_data, fields=fields
    )
    await state.set_state(None)


@update_router.callback_query(F.data == "age")
async def update_age_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    await delete_message_and_reply(call=call, text="Введите новую дату рождения", reply_markup=reply.back_to_menu())
    await state.set_state(states.UpdateProfileSG.age)


@update_router.message(F.text, StateFilter(states.UpdateProfileSG.age))
async def input_age_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    await update_profile_and_send_menu(
        state=state, message=message, middleware_data=middleware_data, fields={"birthdate": message.text}
    )
    await state.set_state(None)


@update_router.callback_query(F.data == "about_me")
async def update_about_me_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    await delete_message_and_reply(
        call=call, text="Напишите новую информацию о себе", reply_markup=reply.back_to_menu()
    )
    await state.set_state(states.UpdateProfileSG.about_me)


@update_router.message(F.text, StateFilter(states.UpdateProfileSG.about_me))
async def input_about_me_handler(message: types.Message, state: FSMContext, **middleware_data: Any) -> None:
    await update_profile_and_send_menu(
        state=state, message=message, middleware_data=middleware_data, fields={"description": message.text}
    )
    await state.set_state(None)


@update_router.callback_query(F.data == "photo")
async def update_photo_handler(call: types.CallbackQuery, state: FSMContext, bot: Bot, **middleware_data: Any) -> None:
    que_client: QueClient = middleware_data.get("que-client")
    storage = await state.get_data()
    access_token = storage.get("access_token")
    _, photos = await que_client.get_all_photos_from_db(access_token=access_token)
    media_group = [
        types.InputMediaPhoto(
            media=photo.get("remote_url"),
        )
        for i, photo in enumerate(photos)
    ]
    await call.message.delete()
    await call.message.answer(text="ㅤ", reply_markup=types.ReplyKeyboardRemove())
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id + 1)
    await call.message.answer_media_group(
        media=media_group,
    )
    await call.message.answer(text=messages.update_profile, reply_markup=inline.photo_update_menu(photos=photos))
