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
    _, profile = await que_client.get_profile(user_id=storage.get("id"), access_token=storage.get("access_token"))
    # await call.message.delete()
    # await call.message.answer_photo()
    await call.message.edit_text(
        text="Ваш профиль: {profile_id}".format(profile_id=profile.get("id")), reply_markup=inline.profile_menu()
    )


@profile_router.callback_query(F.data == "user:profile-create")
@profile_router.message(F.text == "<< Вернуться назад", StateFilter(states.RegistrationSG.gender))
async def profile_create_handler(obj: types.CallbackQuery | types.Message, state: FSMContext) -> None:
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
@profile_router.callback_query(F.data == "get_name_from_tg", StateFilter(states.RegistrationSG.first_name))
async def input_first_name_handler(obj: types.Message | types.CallbackQuery, state: FSMContext) -> None:
    text = "Принято! Выберите ваш гендер"
    first_name: str

    if isinstance(obj, types.Message):
        first_name = obj.text
        await state.update_data({"first_name": first_name})
        await obj.answer(text=text, reply_markup=reply.gender_menu())

    if isinstance(obj, types.CallbackQuery):
        first_name = obj.from_user.first_name
        await state.update_data({"first_name": first_name})
        await obj.message.delete()
        await obj.message.answer(text=text, reply_markup=reply.gender_menu())
    await state.set_state(states.RegistrationSG.gender)


@profile_router.message(F.text == "♂ Мужской", StateFilter(states.RegistrationSG.gender))
@profile_router.message(F.text == "♀ Женский", StateFilter(states.RegistrationSG.gender))
@profile_router.message(F.text == "<< Вернуться назад", StateFilter(states.RegistrationSG.about_me))
async def input_gender_handler(message: types.Message, state: FSMContext) -> None:
    genders = {
        "♂ Мужской": "male",
        "♀ Женский": "female"
    }
    if genders.get(message.text):
        await state.update_data({"gender": genders[message.text]})
    text = (
        "Нажмите на кнопку ниже, чтобы определить ваше местоположение! Или напишите текстом"
    )
    # TODO: Добавить кнопку назад
    await message.answer(text=text, reply_markup=reply.get_location_menu())
    await state.set_state(states.RegistrationSG.city)


@profile_router.message(F.text, StateFilter(states.RegistrationSG.city))
@profile_router.message(F.text == "<< Вернуться назад", StateFilter(states.RegistrationSG.interested_in))
async def input_city_handler(message: types.Message, state: FSMContext) -> None:
    await state.update_data({"city": message.text})
    text = (
        "Отлично! Теперь напишите о себе"
    )
    await message.answer(text=text, reply_markup=reply.back_to_menu())
    await state.set_state(states.RegistrationSG.about_me)


@profile_router.message(F.text, StateFilter(states.RegistrationSG.about_me))
@profile_router.message(F.text == "<< Вернуться назад", StateFilter(states.RegistrationSG.hobbies))
async def input_about_me_handler(message: types.Message, state: FSMContext) -> None:
    await state.update_data({"description": message.text})
    text = "Принято! Теперь выберите кого вы бы хотели найти"
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
    genders = {
        "♂ Парня": "male",
        "♀ Девушку": "female",
    }
    gender = message.text
    if genders.get(gender):
        await state.update_data({"interested_in": genders[gender]})
    text = (
        "Отлично! Выберите интересные для вас занятия"
    )
    await message.answer(text=text, reply_markup=reply.hobbies_menu())
    await state.set_state(states.RegistrationSG.hobbies)


@profile_router.message(F.text, StateFilter(states.RegistrationSG.hobbies))
async def input_hobbies_handler(message: types, state: FSMContext) -> None:
    storage = await state.get_data()
    selected_interests = storage.get("hobbies", [])
    hobby_name = message.text
    text = (
        "И напоследок, пришлите одну или несколько своих фотографий"
    )
    if hobby_name == "Подтвердить выбор":
        if len(selected_interests) == 0:
            await message.answer(text="Вы должны выбрать как минимум один интерес")
        else:
            await message.answer(text=text, reply_markup=reply.get_photo_from_user_menu())
            await state.set_state(states.RegistrationSG.photos)
    elif hobby_name == "Очистить список":
        selected_interests = []
        await state.update_data({"hobbies": selected_interests})
    else:
        selected_interests.append(hobby_name)
        await state.update_data({"hobbies": selected_interests})


# TODO: Дописать
@profile_router.message(
    F.content_type.in_([ContentType.PHOTO]),
    StateFilter(states.RegistrationSG.photos),
)
async def user_handle_album(
        message: types.Message,
        state: FSMContext,
        bot: Bot
) -> None:
    print(await state.get_data())
    # tg_id = message.from_user.id
    # root = "environ.Path(__file__) - 3"
    # user_folder = rf"{root}/photos/{tg_id}/"
    # if not os.path.exists(user_folder):
    #     os.mkdir(user_folder)
    # file_id = message.photo[-1].file_id

    # file = await bot.get_file(file_id=file_id)
    # file_name = f"photo_{file_id}.jpg"
    # file_destination = os.path.join(user_folder, file_name)
    # await bot.download_file(file_path=file.file_path, destination=file_destination)
    # logging.info("Фотографии сохранены")
    # data = await state.get_data()
    # await message.answer_photo(
    #     photo=file_id, caption=render_template(name="profile.html", user=data),
    #     reply_markup=await confirm_keyboard()
    # )
    # await state.update_data(
    #     {
    #         "file_id1": file_id,
    #         "folder": user_folder,
    #         "destination": file_destination
    #     }
    # )

    # await state.set_state(UserFormState.confirm_registration)

# @profile_router.callback_query(
#     inline.HobbiesCallbackFactory.filter(F.action == "toggle" or F.action == "confirm"),
#     StateFilter(states.RegistrationSG.hobbies)
# )
# async def choose_hobbies_handler(
#         call: types.CallbackQuery,
#         state: FSMContext,
#         callback_data: inline.HobbiesCallbackFactory,
#         bot: Bot,
# ) -> None:
#     action = callback_data.action
#     hobby_name = callback_data.hobby_name
#     user_data = await state.get_data()
#     selected_interests = user_data.get("selected_interests", [])
#     if action == "toggle":
#         keyboard = inline.hobbies_menu()
#
#         for row_button in keyboard.inline_keyboard:
#             for button in row_button:
#                 if hobby_name in selected_interests
#                 and hobby_name in button.callback_data and button.text.startswith("🔘"):
#                     button_text = button.text.replace("🔘", "⚪️")
#                     button.text = button_text
#                     selected_interests.remove(hobby_name)
#                     print(selected_interests)
#                     await state.update_data(selected_interests=selected_interests)
#                 if hobby_name in button.callback_data and hobby_name not in selected_interests:
#                     selected_interests.append(hobby_name)
#                     button_text = button.text.replace("⚪️", "🔘")
#                     button.text = button_text
#
#         await state.update_data(selected_interests=selected_interests)
#         # print(selected_interests)
#         await bot.edit_message_reply_markup(
#             chat_id=call.from_user.id,
#             message_id=call.message.message_id,
#             reply_markup=keyboard,
#         )
#     elif action == "confirm":
#         text = (
#             "И напоследок, пришлите мне ваши фотографии, которые будут отображаться в анкете (от 1 до 5)"
#         )
#         await call.message.edit_text(text=text)
#         await state.set_state(states.RegistrationSG.photos)
#     print(user_data)
