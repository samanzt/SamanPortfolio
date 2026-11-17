from telegram import Update
from telegram.ext import ContextTypes

from keyboards.public import main_menu_keyboard


async def select_language(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    await query.answer()

    language = query.data.split("_")[1]

    # ذخیره زبان انتخاب‌شده برای ادامه تعامل کاربر
    context.user_data["language"] = language

    if language == "fa":
        welcome_message = "زبان فارسی انتخاب شد. خوش اومدی! 🇮🇷"
    else:
        welcome_message = "English language selected. Welcome! 🇬🇧"


    await query.message.reply_text(
        welcome_message,
        reply_markup=main_menu_keyboard(language)
 )