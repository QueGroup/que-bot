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


def gender_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(
        types.KeyboardButton(text="♂ Мужской"),
        types.KeyboardButton(text="♀ Женский"),
    )

    return builder.as_markup(resize_keyboard=True)


def interested_in_gender_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(
        types.KeyboardButton(text="♂ Парня"),
        types.KeyboardButton(text="♀ Девушку"),
    )

    return builder.as_markup(resize_keyboard=True)


def hobbies_menu() -> types.ReplyKeyboardMarkup:
    hobbies = [
        ("Спорт", "sports"),
        ("Музыка", "music"),
        ("Путешествия", "travelling"),
        ("Готовка", "cooking"),
        ("Компьютерные игры", "gaming")
    ]
    builder = ReplyKeyboardBuilder()

    for hobby_name, hobby_callback in hobbies:
        button_text = f"{hobby_name}"
        builder.row(
            types.KeyboardButton(text=button_text)
        )
        builder.adjust(1, 2)
    builder.row(
        types.KeyboardButton(text="Подтвердить выбор"),
    )
    return builder.as_markup(resize_keyboard=True)
