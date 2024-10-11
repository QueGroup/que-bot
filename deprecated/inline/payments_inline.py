from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from loader import (
    _,
)
from yarl import (
    URL,
)


async def payment_menu_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    yoomoney = InlineKeyboardButton(text=_("💳 ЮMoney"), callback_data="Yoomoney")
    markup.add(yoomoney)
    return markup


async def yoomoney_keyboard(url: str | URL = None) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    pay_yoomoney = InlineKeyboardButton(text=_("💳 Оплатить"), url=url)
    check_prices = InlineKeyboardButton(
        text=_("🔄 Проверить оплату"), callback_data="Yoomoney:check_payment"
    )
    markup.add(pay_yoomoney, check_prices)
    return markup
