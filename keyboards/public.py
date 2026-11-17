from telegram import ReplyKeyboardMarkup


def main_menu_keyboard(language="fa"):
    if language == "fa":
        keyboard = [
            ["درباره من", "مهارت‌ها"],
            ["پروژه‌ها"],
            ["اطلاعات تماس", "دریافت رزومه"]
        ]

    else:
        keyboard = [
            ["About Me", "Skills"],
            [ "Projects"],
            ["Contact", "Download Resume"]
        ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )