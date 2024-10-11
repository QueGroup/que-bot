import random
import secrets

from aiogram.types import (
    CallbackQuery,
)
from aiogram.utils.exceptions import (
    BadRequest,
)
from loader import (
    bot,
)

from deprecated.get_next_user_func import (
    get_next_user,
)
from deprecated.send_form_func import (
    send_questionnaire,
)
from src.tgbot.keyboards.inline.questionnaires_inline import (
    questionnaires_keyboard,
)


async def create_questionnaire(
        form_owner: int,
        chat_id: int,
        add_text: str | None = None,
        monitoring: bool = False,
        report_system: bool = False,
) -> None:
    markup = await questionnaires_keyboard(target_id=form_owner, monitoring=monitoring)
    await send_questionnaire(
        chat_id=chat_id,
        markup=markup,
        add_text=add_text,
        monitoring=monitoring,
        report_system=report_system,
        owner_id=form_owner,
    )


async def create_questionnaire_reciprocity(
        liker: int, chat_id: int, add_text: str = None
) -> None:
    await send_questionnaire(chat_id=chat_id, add_text=add_text, owner_id=liker)


async def monitoring_questionnaire(call: CallbackQuery) -> None:
    telegram_id = call.from_user.id
    user_list = await get_next_user(telegram_id, monitoring=True)
    random_user = random.choice(user_list)
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id, message_id=call.message.message_id
    )
    try:
        await create_questionnaire(
            form_owner=random_user, chat_id=telegram_id, monitoring=True
        )
    except BadRequest:
        await create_questionnaire(
            form_owner=random_user, chat_id=telegram_id, monitoring=True
        )


async def rand_user_list(call: CallbackQuery) -> int:
    user_list = await get_next_user(call.from_user.id)
    random_user_list = [random.choice(user_list) for _ in range(len(user_list))]
    random_user = secrets.choice(random_user_list)
    return random_user
