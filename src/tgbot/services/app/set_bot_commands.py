import logging

from aiogram import (
    types, Bot,
)

from src.tgbot.config import (
    Config,
)


async def set_user_commands(
        bot: Bot, user_id: int, commands: list[types.BotCommand]
):
    try:
        await bot.set_my_commands(
            commands=commands, scope=types.BotCommandScopeChat(chat_id=user_id)
        )
    except Exception as ex:
        logging.error(f"{user_id}: Commands are not installed. {ex}")


async def set_default_commands(bot: Bot, config: Config) -> None:
    default_commands = [
        types.BotCommand(command="start", description="🟢 Запустить бота"),
        types.BotCommand(command="catalog", description="🏪 Открыть каталог"),
        types.BotCommand(command="profile", description="👨 Личный кабинет"),
        types.BotCommand(command="order", description="🚚 Статус заказа"),
        types.BotCommand(command="cart", description="📂 Корзина"),
    ]

    admin_commands = [
        types.BotCommand(command="admin", description="⚒ Админ-Меню"),
        types.BotCommand(command="users", description="🫂 Пользователи"),
        types.BotCommand(command="settings", description="⚙️ Настройки"),
        types.BotCommand(command="logs", description="🗒 Логи"),
    ]

    await bot.set_my_commands(default_commands, scope=types.BotCommandScopeDefault())

    for admin_id in config.tg_bot.admin_ids:
        await set_user_commands(
            bot=bot,
            user_id=admin_id,
            commands=admin_commands + default_commands
        )
