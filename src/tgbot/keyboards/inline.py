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
        types.InlineKeyboardButton(text=_("👤 Мой профиль"), callback_data="user:profile"),
    )
    builder.row(
        types.InlineKeyboardButton(text=_("Изменить"), callback_data="user:edit"),
        types.InlineKeyboardButton(text=_("Устройства"), callback_data="user:session")
    )
    builder.row(
        types.InlineKeyboardButton(text=_("🔙 Выйти из аккаунта"), callback_data="user:signout")
    )

    return builder.as_markup()


def user_activation_menu() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text=_("🚀 Активировать"), callback_data="user:activate")
    )
    return builder.as_markup()


def profile_menu() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Изменить", callback_data="profile:edit"),
        types.InlineKeyboardButton(text="Удалить", callback_data="profile:delete")
    )
    builder.row(
        types.InlineKeyboardButton(text="<< Вернуться назад", callback_data="back_to_user_menu")
    )
    return builder.as_markup()
