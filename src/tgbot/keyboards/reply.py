from aiogram import (
    types,
)
from aiogram.types import (
    WebAppInfo,
)
from aiogram.utils.i18n import (
    gettext as _,
)
from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder,
)


def main_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text=_("👤 Аккаунт"))
    )
    builder.row(
        types.KeyboardButton(text=_("💜 Знакомства")),
        types.KeyboardButton(text=_("🎭 Мероприятия")),
    )
    builder.row(
        types.KeyboardButton(text=_("ℹ️ О проекте"))
    )
    return builder.as_markup(resize_keyboard=True)


def login_signup_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text=_("📝 Создать аккаунт")),
        types.KeyboardButton(text=_("🔑 Войти в аккаунт"), web_app=WebAppInfo(url="https://floppy-phones-camp.loca.lt")),
    )
    return builder.as_markup(resize_keyboard=True)
