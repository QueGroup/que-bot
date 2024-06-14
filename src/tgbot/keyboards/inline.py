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
            types.InlineKeyboardButton(text=_("👤 Мой профиль"), callback_data="user:profile"),
        )
    else:
        builder.row(
            types.InlineKeyboardButton(text=_("Создать профиль"), callback_data="user:profile-create"),
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

# TODO: Может понадобится когда-нибудь
# class HobbiesCallbackFactory(CallbackData):
#     action: str
#     hobby_name: str | None = None
#
#
# def hobbies_menu() -> types.InlineKeyboardMarkup:
#     hobbies = [
#         ("Спорт", "sports"),
#         ("Музыка", "music"),
#         ("Путешествия", "travelling"),
#         ("Готовка", "cooking"),
#         ("Компьютерные игры", "gaming")
#     ]
#     builder = InlineKeyboardBuilder()
#
#     for hobby_name, hobby_callback in hobbies:
#         button_text = f"⚪️ {hobby_name}"
#         builder.button(
#             text=button_text,
#             callback_data=HobbiesCallbackFactory(action="toggle", hobby_name=hobby_callback)
#         )
#         builder.adjust(2)
#     builder.button(
#         text="Подтвердить выбор", callback_data=HobbiesCallbackFactory(action="confirm")
#     )
#     return builder.as_markup()
