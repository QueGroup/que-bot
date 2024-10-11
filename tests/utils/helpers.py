# tests/helpers.py

from typing import (
    Optional,
)

from telethon.tl.custom.message import (
    Message,
    MessageButton,
)


def get_button_with_text(
        message: Message, text: str, strict: bool = False
) -> Optional[MessageButton]:
    """Return MessageButton from Message with text or None."""
    if message.buttons is None:
        return None

    for row in message.buttons:
        for button in row:
            if strict:
                is_match = text == button.text
            else:
                is_match = text in button.text
            if is_match:
                return button

    return None
