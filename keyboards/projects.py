
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def projects_keyboard(projects, language="fa"):
    keyboard = []

    for project in projects:
        if language == "fa":
            name = project["name_fa"]
        else:
            name = project["name_en"]

        keyboard.append([
            InlineKeyboardButton(
                name,
                callback_data=f"project_{project['id']}"
            )
        ])

    return InlineKeyboardMarkup(keyboard)
