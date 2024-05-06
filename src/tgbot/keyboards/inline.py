from aiogram import (
    types,
)
from aiogram.types import (
    WebAppInfo,
)
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
)


def about_project_menu() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔗 Github", web_app=WebAppInfo(url="https://github.com/QueGroup"))
    )
    return builder.as_markup()


def user_menu() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="👤 Мой профиль", callback_data="user:profile")
    )
    builder.row(
        types.InlineKeyboardButton(text="🔙 Выйти из аккаунта", callback_data="user:signout")
    )

    return builder.as_markup()


def user_activation_menu() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🚀 Активировать", callback_data="user:activate")
    )
    return builder.as_markup()
