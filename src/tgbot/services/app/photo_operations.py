import asyncio
import pathlib

from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    InlineKeyboardMarkup,
    InputFile,
    Message,
    ReplyKeyboardRemove,
)

from loader import (
    _,
    bot,
    logger,
)
from src.infrastructure.db_api import (
    db_commands,
)
from src.tgbot.services.app.message_operations import (
    finished_registration,
)


async def saving_normal_photo(
        message: Message, telegram_id: int, file_id: str, state: FSMContext
) -> None:
    """Функция, сохраняющая фотографию пользователя без цензуры."""
    try:
        await db_commands.update_user_data(telegram_id=telegram_id, photo_id=file_id)

        await message.answer(
            text=_("Фото принято!"), reply_markup=ReplyKeyboardRemove()
        )
    except Exception as err:
        logger.info(f"Ошибка в saving_normal_photo | err: {err}")
        await message.answer(
            text=_(
                "Произошла ошибка! Попробуйте еще раз либо отправьте другую фотографию. \n"
                "Если ошибка осталась, напишите агенту поддержки."
            )
        )
    await finished_registration(state=state, telegram_id=telegram_id, message=message)


async def saving_censored_photo(
        message: Message,
        telegram_id: int,
        state: FSMContext,
        out_path: str | pathlib.Path,
        flag: str | None = "registration",
        markup: InlineKeyboardMarkup | None = None,
) -> None:
    """.Функция, сохраняющая фотографию пользователя с цензурой."""
    photo = InputFile(out_path)
    id_photo = await bot.send_photo(
        chat_id=telegram_id,
        photo=photo,
        caption=_(
            "Во время проверки вашего фото мы обнаружили подозрительный контент!\n"
            "Поэтому мы чуть-чуть подкорректировали вашу фотографию"
        ),
    )
    file_id = id_photo["photo"][0]["file_id"]
    await asyncio.sleep(1)
    try:
        await db_commands.update_user_data(telegram_id=telegram_id, photo_id=file_id)

    except Exception as err:
        logger.info(f"Ошибка в saving_censored_photo | err: {err}")
        await message.answer(
            text=_(
                "Произошла ошибка!"
                " Попробуйте еще раз либо отправьте другую фотографию. \n"
                "Если ошибка осталась, напишите агенту поддержки."
            )
        )
    if flag == "change_datas":
        await message.answer(
            text=_("<u>Фото принято!</u>\n" "Выберите, что вы хотите изменить: "),
            reply_markup=markup,
        )
        await state.reset_state()
    elif flag == "registration":
        await finished_registration(
            state=state, telegram_id=telegram_id, message=message
        )


async def update_normal_photo(
        message: Message,
        telegram_id: int,
        file_id: str,
        state: FSMContext,
        markup
) -> None:
    """Функция, которая обновляет фотографию пользователя."""
    try:
        await db_commands.update_user_data(telegram_id=telegram_id, photo_id=file_id)
        await message.answer(
            text=_("Фото принято!"), reply_markup=ReplyKeyboardRemove()
        )
        await asyncio.sleep(3)
        await message.answer(
            text=_("Выберите, что вы хотите изменить: "), reply_markup=markup
        )
        await state.reset_state()
    except Exception as err:
        logger.info(f"Ошибка в update_normal_photo | err: {err}")
        await message.answer(
            text=_(
                "Произошла ошибка! Попробуйте еще раз либо отправьте другую фотографию. \n"
                "Если ошибка осталась, напишите агенту поддержки."
            )
        )
