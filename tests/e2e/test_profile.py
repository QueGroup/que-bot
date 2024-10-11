import asyncio

from aiogram import (
    types,
)
import pytest
from telethon import (
    functions,
)
from telethon.tl.custom import (
    Conversation,
)


@pytest.mark.anyio
async def test_create_profile(conv: Conversation) -> None:
    await conv.send_message("/start")
    start_resp: types.Message = await conv.get_response()
    await conv.send_message("👤 Аккаунт")
    acc_resp: types.Message = await conv.get_response()
    button = acc_resp.buttons[0][0]
    button_data = button.data
    # https://github.com/LonamiWebs/Telethon/issues/326
    create_profile_task = asyncio.create_task(
        conv._client(functions.messages.GetBotCallbackAnswerRequest(
            peer=acc_resp.peer_id,
            msg_id=acc_resp.id,
            data=button_data
        ))
    )
    await asyncio.sleep(1)
    if not create_profile_task.done():
        pass

    await conv.send_message("Борис")
    await asyncio.sleep(0.1)
    gender_resp: types.Message = await conv.get_response()
    assert "Выберите ваш гендер" in gender_resp.text
    await conv.send_message("♂ Мужской")
    await asyncio.sleep(0.1)
    dob_prompt_resp: types.Message = await conv.get_response()
    assert "выберите дату своего рождения" in dob_prompt_resp.text
    calendar_resp: types.Message = await conv.get_response()
    calendar_year_task = asyncio.create_task(conv._client(functions.messages.GetBotCallbackAnswerRequest(
        peer=calendar_resp.peer_id,
        msg_id=calendar_resp.id,
        data=b"dialog_calendar:SET-YEAR:2004:-1:-1"
    )))
    await conv.send_message(".")  # TODO: Без этого кнопки не обрабатываются
    await asyncio.sleep(0.25)

    calendar_month_task = asyncio.create_task(conv._client(functions.messages.GetBotCallbackAnswerRequest(
        peer=calendar_resp.peer_id,
        msg_id=calendar_resp.id,
        data=b"dialog_calendar:SET-MONTH:2004:1:-1"
    )))
    await conv.send_message(".")
    await asyncio.sleep(0.25)
    calendar_day_task = asyncio.create_task(conv._client(functions.messages.GetBotCallbackAnswerRequest(
        peer=calendar_resp.peer_id,
        msg_id=calendar_resp.id,
        data=b"dialog_calendar:SET-DAY:2004:1:1"
    )))
    await conv.send_message(".")
    await asyncio.sleep(0.25)
    city_prompt_resp: types.Message = await conv.get_response()
    assert "Нажмите на кнопку ниже, чтобы определить ваше местоположение" in city_prompt_resp.text
    await conv.send_message("Пенза")
    await asyncio.sleep(0.25)
    confirm_city_resp: types.Message = await conv.get_response()
    assert "Я нашел такой адрес" in confirm_city_resp.text

    await conv.send_message("✅ Да все хорошо!")
    await asyncio.sleep(0.25)
    about_me_prompt_resp: types.Message = await conv.get_response()
    assert "напишите о себе" in about_me_prompt_resp.text
    await conv.send_message("Описание о себе")
    await asyncio.sleep(0.25)
    interested_in_prompt_resp: types.Message = await conv.get_response()
    assert "кого вы бы хотели найти" in interested_in_prompt_resp.text
    await conv.send_message("♀ Девушку")
    await asyncio.sleep(0.25)
    hobbies_prompt_resp: types.Message = await conv.get_response()
    assert "Выберите интересные для вас занятия" in hobbies_prompt_resp.text
    await conv.send_message("Чтение")
    await asyncio.sleep(0.25)
    await conv.send_message("Подтвердить выбор")
    await asyncio.sleep(0.25)
    photo_prompt_resp: types.Message = await conv.get_response()

    photo_file_id = "https://t3.ftcdn.net/jpg/01/42/62/84/360_F_142628436_BdXXMV34Xf665lwSRmBbAVICjFXh7vG9.jpg"
    await conv.send_file(photo_file_id)
    confirmation_prompt_resp: types.Message = await conv.get_response()
    await asyncio.sleep(0.25)
    await conv.send_message("✅ Да все хорошо!")
    await asyncio.sleep(0.25)
    final_resp: types.Message = await conv.get_response()

    assert "Поздравляем, вы создали профиль" in final_resp.text


@pytest.mark.anyio
async def test_get_profile(conv: Conversation):
    await conv.send_message("/start")
    start_resp: types.Message = await conv.get_response()
    await conv.send_message("👤 Аккаунт")
    acc_resp: types.Message = await conv.get_response()
    button = acc_resp.buttons[0][0]
    button_data = button.data
    create_profile_task = asyncio.create_task(
        conv._client(functions.messages.GetBotCallbackAnswerRequest(
            peer=acc_resp.peer_id,
            msg_id=acc_resp.id,
            data=button_data
        ))
    )
    await asyncio.sleep(1)
    if not create_profile_task.done():
        pass
    _: types.Message = await conv.get_response()
    profile_resp: types.Message = await conv.get_response()

    assert "Имя:" in profile_resp.text
    assert "Пол:" in profile_resp.text
    assert "Дата рождения:" in profile_resp.text
    assert "Город:" in profile_resp.text
    assert "О себе:" in profile_resp.text
    assert "Хочешь найти:" in profile_resp.text
    assert "Хобби:" in profile_resp.text

    assert profile_resp.photo is not None, "Фото профиля отсутствует"
