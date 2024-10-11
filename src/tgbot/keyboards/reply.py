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
    builder.row(
        types.KeyboardButton(text=_("💜 Знакомства"))
    )
    builder.add(
        types.KeyboardButton(text=_("👤 Аккаунт"))
    )
    builder.row(
        types.KeyboardButton(text=_("ℹ️ О проекте"))
    )
    builder.adjust(1, 2)
    return builder.as_markup(resize_keyboard=True)


def login_signup_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text=_("📝 Создать аккаунт")),
        types.KeyboardButton(
            text=_("🔑 Войти в аккаунт"), web_app=WebAppInfo(url="https://petite-wasps-play.loca.lt")
        ),
    )
    return builder.as_markup(resize_keyboard=True)


def login_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(
            text=_("🔑 Войти в аккаунт"), web_app=WebAppInfo(url="https://petite-wasps-play.loca.lt")
        ),
    )
    return builder.as_markup(resize_keyboard=True)


def gender_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="♂ Мужской"),
        types.KeyboardButton(text="♀ Женский"),
    )
    builder.row(
        types.KeyboardButton(text="<< Вернуться назад")
    )
    return builder.as_markup(resize_keyboard=True)


def interested_in_gender_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="♂ Парня"),
        types.KeyboardButton(text="♀ Девушку"),
    )
    builder.row(
        types.KeyboardButton(text="<< Вернуться назад")
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
        types.KeyboardButton(text="Очистить список"),
        types.KeyboardButton(text="<< Вернуться назад")
    )
    return builder.as_markup(resize_keyboard=True)


def get_location_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(
            text=_("🗺 Определить автоматически"), request_location=True
        ),
        types.KeyboardButton(text="<< Вернуться назад")
    )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_photo_from_user_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="<< Вернуться назад")
    )
    return builder.as_markup(resize_keyboard=True)


def get_user_first_name() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Взять из телеграмма")
    )
    builder.row(
        types.KeyboardButton(text="<< Вернуться назад")
    )
    return builder.as_markup(resize_keyboard=True)


def back_to_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="<< Вернуться назад")
    )
    return builder.as_markup(resize_keyboard=True)


def confirmation_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="✅ Да все хорошо!")
    )
    return builder.as_markup(resize_keyboard=True)


def profile_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="✏️ Изменить"),
        types.KeyboardButton(text="🗑 Удалить")
    )
    builder.row(
        types.KeyboardButton(text="<< Вернуться назад")
    )
    return builder.as_markup(resize_keyboard=True)
