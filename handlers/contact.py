from telegram import Update
from telegram.ext import ContextTypes


async def show_contact(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    language = context.user_data.get("language", "fa")

    if language == "fa":
        message = (
            "📞 راه‌های ارتباطی با من\n\n"
            "💬 تلگرام: @samanzt5\n"
            "📱 موبایل: 09914664198\n"
            "📧 ایمیل: ziaratisaman@gmail.com"
        )
    else:
        message = (
            "📞 Contact Information\n\n"
            "💬 Telegram: @samanzt5\n"
            "📱 Phone: 09914664198\n"
            "📧 Email: ziaratisaman@gmail.com"
        )

    await update.message.reply_text(message)