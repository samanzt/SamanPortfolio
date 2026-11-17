from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def language_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)