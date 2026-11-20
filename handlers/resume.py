
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes


BASE_DIR = Path(__file__).resolve().parent.parent
RESUME_PATH = BASE_DIR / "assets" / "resume.pdf"


async def send_resume(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    language = context.user_data.get("language", "fa")

    if not RESUME_PATH.exists():
        message = (
            "فایل رزومه در حال حاضر در دسترس نیست."
            if language == "fa"
            else "The resume file is currently unavailable."
        )
        await update.message.reply_text(message)
        return

    caption = (
        "رزومه من به زبان فارسی و انگلیسی"
        if language == "fa"
        else "My resume in Persian and English"
    )

    await update.message.reply_document(
        document=RESUME_PATH.open("rb"),
        filename="resume.pdf",
        caption=caption
    )
