from telegram import Update
from telegram.ext import ContextTypes


async def show_about(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    language = context.user_data.get("language", "fa")

    if language == "fa":
        message = (
            "سلام! من سامان هستم. 👋\n\n"
            "💻 درباره من\n"
            "من علاقه‌مند به برنامه‌نویسی Python و توسعه نرم‌افزار هستم. "
            "در حال یادگیری توسعه بک‌اند، کار با APIها و ساخت ربات‌های تلگرامی هستم.\n\n"
            "🚀 مسیر حرفه‌ای\n"
            "تمرکزم روی ساخت پروژه‌های کاربردی، توسعه مهارت‌های فنی "
            "و کسب تجربه در پروژه‌های واقعی است.\n\n"
            "🎯 هدف من\n"
            "می‌خواهم دانش برنامه‌نویسی خودم را به مهارت‌های حرفه‌ای "
            "تبدیل کنم و در پروژه‌های واقعی فعالیت داشته باشم."
        )

    else:
        message = (
            "Hello! I'm Saman. 👋\n\n"
            "💻 About Me\n"
            "I'm interested in Python programming and software development. "
            "I'm currently learning backend development, working with APIs, "
            "and building Telegram bots.\n\n"
            "🚀 Professional Journey\n"
            "I focus on building practical projects, improving my technical "
            "skills, and gaining experience through real-world projects.\n\n"
            "🎯 My Goal\n"
            "I aim to turn my programming knowledge into professional skills "
            "and contribute to real-world projects."
        )

    await update.message.reply_text(message)