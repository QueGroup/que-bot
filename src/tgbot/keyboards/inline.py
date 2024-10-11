from aiogram import (
    types,
)
from aiogram.filters.callback_data import (
    CallbackData,
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
            types.InlineKeyboardButton(text=_("📝 Создать профиль"), callback_data="user:profile-create"),
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
        types.InlineKeyboardButton(text=_("🎂 Возраст"), callback_data="age"),
        types.InlineKeyboardButton(text=_("📸 Фото"), callback_data="photo"),
        types.InlineKeyboardButton(text=_("✍️ О себе"), callback_data="about_me"),
        types.InlineKeyboardButton(text=_("🧑‍🎨 Хобби"), callback_data="hobbies"),
        types.InlineKeyboardButton(text=_("<< Вернуться назад"), callback_data="back_to_profile")
    )
    builder.adjust(1, 2, 1, 2, 1, 1)
    return builder.as_markup()


class PhotoCallbackFactory(CallbackData, prefix="menu"):  # type: ignore
    photo_id: int


def photo_update_menu(photos: list[dict[str, str]]) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for i in range(len(photos)):
        builder.button(
            text=f"{i + 1}",
            callback_data=PhotoCallbackFactory(photo_id=photos[i].get("id")).pack(),
        )
    builder.row(
        types.InlineKeyboardButton(text=_("<< Вернуться назад"), callback_data="back_to_profile")
    )
    builder.adjust(1)
    return builder.as_markup()
