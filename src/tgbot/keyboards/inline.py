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


def user_menu(is_profile: bool) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_profile:
        builder.row(
            types.InlineKeyboardButton(text=_("👤 Профиль"), callback_data="user:profile"),
        )
    else:
        builder.row(
            types.InlineKeyboardButton(text=_("Создать профиль"), callback_data="user:profile-create"),
        )
    builder.row(
        types.InlineKeyboardButton(text=_("Изменить"), callback_data="user:edit"),
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


def profile_update_menu() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(text=_("📇 Имя"), callback_data="first_name"),
        types.InlineKeyboardButton(text=_("⚧️ Пол"), callback_data="gender"),
        types.InlineKeyboardButton(text=_("🏙️ Город"), callback_data="city"),
        types.InlineKeyboardButton(text=_("🎂 Дата рождения"), callback_data="birthdate"),
        types.InlineKeyboardButton(text=_("📸 Фото"), callback_data="photo"),
        types.InlineKeyboardButton(text=_("✍️ О себе"), callback_data="about_me"),
        types.InlineKeyboardButton(text=_("🧑‍🎨 Хобби"), callback_data="hobbies")
    )
    builder.adjust(1, 2, 1, 2)
    return builder.as_markup()
