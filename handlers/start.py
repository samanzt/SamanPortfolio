
from telegram import Update
from telegram.ext import ContextTypes

from keyboards.language import language_keyboard
from database.stats import track_event


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    track_event(update.effective_user, "start")

    await update.message.reply_text(
        "سلام! 👋\n"
        "به دنیای تخصص و تجربه من خوش اومدی.\n\n"
        "لطفاً زبان موردنظرت رو انتخاب کن:",
        reply_markup=language_keyboard()
    )
