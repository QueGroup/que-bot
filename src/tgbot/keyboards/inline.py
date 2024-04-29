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
        types.InlineKeyboardButton(text="Github", web_app=WebAppInfo(url="https://github.com/QueGroup"))
    )
    return builder.as_markup()


def user_menu(is_active: bool) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔁 Изменить", callback_data="user:update"),
    )

    return builder.as_markup()


def user_activation_menu() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔛 Активировать", callback_data="user:activate")
    )
    return builder.as_markup()
