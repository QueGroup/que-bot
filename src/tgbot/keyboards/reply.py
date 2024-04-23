from aiogram import (
    types,
)
from aiogram.types import (
    WebAppInfo,
)
from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder,
)


def main_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="👤 Аккаунт")
    )
    builder.row(
        types.KeyboardButton(text="💜 Знакомства"),
        types.KeyboardButton(text="🎭 Мероприятия"),
    )
    builder.row(
        types.KeyboardButton(text="❔ О проекте")
    )
    return builder.as_markup(resize_keyboard=True)


def login_signup_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="✏️ Создать аккаунт"),
        types.KeyboardButton(text="🛂 Войти в аккаунт", web_app=WebAppInfo(url="https://light-clouds-sleep.loca.lt")),
    )
    return builder.as_markup(resize_keyboard=True)
