from telegram import Update
from telegram.ext import ContextTypes


async def show_skills(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    language = context.user_data.get("language", "fa")

    if language == "fa":
        message = (
            "💻 مهارت‌های فنی من\n\n"
            "🐍 Python\n"
            "• برنامه‌نویسی شی‌گرا (OOP)\n"
            "• کار با ساختارهای داده\n"
            "• توسعه ربات‌های تلگرامی\n\n"
            "🤖 Telegram Bot Development\n"
            "• Python Telegram Bot\n"
            "• کار با دکمه‌ها و منوها\n"
            "• مدیریت پیام‌ها و رویدادها\n\n"
            "🔌 API Integration\n"
            "• کار با REST API\n"
            "• استفاده از کتابخانه Requests\n\n"
            "🗄 Database\n"
            "• SQLite\n"
            "• عملیات CRUD\n\n"
            "🛠 Tools\n"
            "• Git و GitHub\n"
            "• کار با محیط مجازی Python"
        )

    else:
        message = (
            "💻 My Technical Skills\n\n"
            "🐍 Python\n"
            "• Object-Oriented Programming (OOP)\n"
            "• Working with Data Structures\n"
            "• Telegram Bot Development\n\n"
            "🤖 Telegram Bot Development\n"
            "• Python Telegram Bot\n"
            "• Inline Keyboards and Menus\n"
            "• Message and Event Handling\n\n"
            "🔌 API Integration\n"
            "• Working with REST APIs\n"
            "• Requests Library\n\n"
            "🗄 Database\n"
            "• SQLite\n"
            "• CRUD Operations\n\n"
            "🛠 Tools\n"
            "• Git and GitHub\n"
            "• Python Virtual Environments"
        )

    await update.message.reply_text(message)