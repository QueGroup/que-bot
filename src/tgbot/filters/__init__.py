from src.tgbot.filters.FiltersChat import (
    IsPrivate,
    IsGroup,
)

from src.tgbot.filters.IsAdminFilter import (
    IsAdmin
)

__all__ = (
    "IsGroup",
    "IsPrivate",
    "IsAdmin",
)

# def setup(dp: Dispatcher):
#     logger.info("Подключение filters...")
#     text_messages = [
#         dp.message_handlers,
#         dp.edited_message_handlers,
#     ]
#     logger.info(text_messages)
#     dp.filters_factory.bind(IsPrivate)
