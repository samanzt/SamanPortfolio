
from pathlib import Path
import sqlite3

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_ID

from database.bots import (
    get_all_bots,
    get_bot,
    add_bot
)

from keyboards.admin import admin_keyboard

from keyboards.bot_manager import (
    bot_manager_keyboard,
    managed_bots_keyboard,
    bot_control_keyboard
)

from services.process_manager import (
    is_running,
    start_bot,
    stop_bot,
    restart_bot
)


# Allowed directories
BOTS_ROOT = Path("/home/samanzti/bots").resolve()
VENVS_ROOT = Path("/home/samanzti/venvs/bots").resolve()


# Conversation states
BOT_NAME = 10
BOT_USERNAME = 11
BOT_PROJECT_PATH = 12
BOT_VENV_PATH = 13
BOT_ENTRY_FILE = 14


def is_admin(update):
    return (
        update.effective_user
        and update.effective_user.id == ADMIN_ID
    )


# -------------------------
# Main Bot Manager
# -------------------------

async def open_bot_manager(update, context):
    query = update.callback_query

    if not is_admin(update):
        await query.answer("دسترسی غیرمجاز", show_alert=True)
        return

    await query.answer()

    language = context.user_data.get("language", "fa")

    text = (
        "🤖 مدیریت ربات‌ها"
        if language == "fa"
        else "🤖 Bot Manager"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=bot_manager_keyboard(language)
    )


async def show_managed_bots(update, context):
    query = update.callback_query

    if not is_admin(update):
        await query.answer("دسترسی غیرمجاز", show_alert=True)
        return

    await query.answer()

    language = context.user_data.get("language", "fa")
    bots = get_all_bots()

    if not bots:
        text = (
            "هنوز هیچ رباتی ثبت نشده است."
            if language == "fa"
            else "No bots have been registered yet."
        )

        await query.edit_message_text(
            text=text,
            reply_markup=bot_manager_keyboard(language)
        )
        return

    text = (
        "🤖 ربات‌های ثبت‌شده:"
        if language == "fa"
        else "🤖 Registered Bots:"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=managed_bots_keyboard(bots, language)
    )


async def select_managed_bot(update, context):
    query = update.callback_query

    if not is_admin(update):
        await query.answer("دسترسی غیرمجاز", show_alert=True)
        return

    await query.answer()

    bot_id = int(query.data.replace("bm_select_", ""))
    bot = get_bot(bot_id)

    if not bot:
        await query.edit_message_text("این ربات پیدا نشد.")
        return

    language = context.user_data.get("language", "fa")
    running = is_running(bot_id)

    text = (
        f"🤖 نام ربات: {bot['name']}\n"
        f"وضعیت: {'🟢 روشن' if running else '🔴 خاموش'}"
        if language == "fa"
        else
        f"🤖 Bot Name: {bot['name']}\n"
        f"Status: {'🟢 Running' if running else '🔴 Stopped'}"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=bot_control_keyboard(
            bot_id,
            running,
            language
        )
    )


async def back_to_admin(update, context):
    query = update.callback_query

    if not is_admin(update):
        await query.answer("دسترسی غیرمجاز", show_alert=True)
        return

    await query.answer()

    language = context.user_data.get("language", "fa")

    await query.edit_message_text(
        "پنل مدیریت" if language == "fa" else "Admin Panel",
        reply_markup=admin_keyboard()
    )


# -------------------------
# Add Bot Conversation
# -------------------------

async def start_add_bot(update, context):
    query = update.callback_query

    if not is_admin(update):
        await query.answer("دسترسی غیرمجاز", show_alert=True)
        return

    await query.answer()

    context.user_data["new_bot"] = {}

    language = context.user_data.get("language", "fa")

    text = (
        "➕ افزودن ربات جدید\n\n"
        "نام دلخواه ربات را وارد کن.\n"
        "برای لغو عملیات، دستور /cancel را بفرست."
        if language == "fa"
        else
        "➕ Add New Bot\n\n"
        "Enter a name for the bot.\n"
        "Send /cancel to cancel."
    )

    await query.message.reply_text(text)

    return BOT_NAME


async def receive_bot_name(update, context):
    if not is_admin(update):
        return

    name = update.message.text.strip()

    if not name or len(name) > 100:
        await update.message.reply_text(
            "نام باید بین ۱ تا ۱۰۰ کاراکتر باشد. دوباره وارد کن:"
        )
        return BOT_NAME

    context.user_data["new_bot"]["name"] = name

    await update.message.reply_text(
        "Username ربات را وارد کن.\n"
        "اگر نمی‌خواهی ثبت شود، علامت - را بفرست:"
    )

    return BOT_USERNAME


async def receive_bot_username(update, context):
    if not is_admin(update):
        return

    username = update.message.text.strip()

    if username == "-":
        username = None
    else:
        username = username.lstrip("@")

        if (
            not username
            or len(username) > 32
            or not username.replace("_", "").isalnum()
        ):
            await update.message.reply_text(
                "Username معتبر نیست. دوباره وارد کن یا - بفرست:"
            )
            return BOT_USERNAME

    context.user_data["new_bot"]["username"] = username

    await update.message.reply_text(
        "مسیر کامل پوشه پروژه روی سرور را وارد کن.\n"
        "مثال:\n"
        "/home/samanzti/bots/my_bot"
    )

    return BOT_PROJECT_PATH


async def receive_bot_project_path(update, context):
    if not is_admin(update):
        return

    path = Path(
        update.message.text.strip()
    ).expanduser()

    resolved_path = path.resolve()

    if (
        not path.is_absolute()
        or not path.is_dir()
        or not resolved_path.is_relative_to(BOTS_ROOT)
        or resolved_path == BOTS_ROOT
    ):
        await update.message.reply_text(
            "مسیر نامعتبر است. پوشه پروژه باید داخل مسیر زیر باشد:\n"
            f"{BOTS_ROOT}\n"
            "دوباره وارد کن:"
        )
        return BOT_PROJECT_PATH

    context.user_data["new_bot"]["project_path"] = str(resolved_path)

    await update.message.reply_text(
        "مسیر کامل محیط مجازی ربات را وارد کن.\n"
        "مثال:\n"
        "/home/samanzti/venvs/bots/my_bot"
    )

    return BOT_VENV_PATH


async def receive_bot_venv_path(update, context):
    if not is_admin(update):
        return

    path = Path(
        update.message.text.strip()
    ).expanduser()

    python_path = path / "bin" / "python"
    resolved_path = path.resolve()

    if (
        not path.is_absolute()
        or not path.is_dir()
        or not python_path.is_file()
        or not resolved_path.is_relative_to(VENVS_ROOT)
        or resolved_path == VENVS_ROOT
    ):
        await update.message.reply_text(
            "محیط مجازی معتبر نیست یا مسیر آن خارج از محدوده مجاز است.\n"
            "محیط مجازی باید داخل مسیر زیر باشد:\n"
            f"{VENVS_ROOT}\n"
            "دوباره مسیر را وارد کن:"
        )
        return BOT_VENV_PATH

    context.user_data["new_bot"]["venv_path"] = str(resolved_path)

    await update.message.reply_text(
        "نام فایل اجرایی ربات را وارد کن.\n"
        "مثال: main.py"
    )

    return BOT_ENTRY_FILE


async def receive_bot_entry_file(update, context):
    if not is_admin(update):
        return

    entry_file = update.message.text.strip()

    project_path = Path(
        context.user_data["new_bot"]["project_path"]
    ).resolve()

    entry_path = (project_path / entry_file).resolve()

    if (
        not entry_path.is_relative_to(project_path)
        or not entry_path.is_file()
        or entry_path.suffix != ".py"
    ):
        await update.message.reply_text(
            "فایل اجرایی معتبر نیست یا پیدا نشد.\n"
            "فقط فایل‌های پایتون با پسوند .py مجاز هستند.\n"
            "مثال: main.py\n"
            "دوباره نام فایل را وارد کن:"
        )
        return BOT_ENTRY_FILE

    data = context.user_data["new_bot"]

    log_path = str(
        Path(data["project_path"]) / "bot.log"
    )

    try:
        bot_id = add_bot(
            name=data["name"],
            username=data["username"],
            project_path=data["project_path"],
            venv_path=data["venv_path"],
            entry_file=entry_file,
            log_path=log_path
        )

    except sqlite3.IntegrityError:
        await update.message.reply_text(
            "این نام قبلاً ثبت شده است. عملیات لغو شد."
        )

        context.user_data.pop("new_bot", None)
        return -1

    context.user_data.pop("new_bot", None)

    language = context.user_data.get("language", "fa")

    text = (
        f"✅ ربات با موفقیت ثبت شد.\n\n"
        f"نام: {data['name']}\n"
        f"شناسه: {bot_id}"
        if language == "fa"
        else
        f"✅ Bot registered successfully.\n\n"
        f"Name: {data['name']}\n"
        f"ID: {bot_id}"
    )

    await update.message.reply_text(text)

    return -1


async def cancel_add_bot(update, context):
    context.user_data.pop("new_bot", None)

    language = context.user_data.get("language", "fa")

    await update.message.reply_text(
        "عملیات افزودن ربات لغو شد."
        if language == "fa"
        else "Bot registration cancelled."
    )

    return -1


# -------------------------
# Bot Start / Stop / Restart
# -------------------------

async def manage_bot_action(update, context):
    query = update.callback_query

    if not is_admin(update):
        await query.answer("دسترسی غیرمجاز", show_alert=True)
        return

    await query.answer()

    action, bot_id_text = query.data.rsplit("_", 1)
    bot_id = int(bot_id_text)

    bot = get_bot(bot_id)

    if not bot:
        await query.edit_message_text("این ربات پیدا نشد.")
        return

    if action == "bm_start":
        success, message = start_bot(bot_id)

    elif action == "bm_stop":
        success, message = stop_bot(bot_id)

    elif action == "bm_restart":
        success, message = restart_bot(bot_id)

    else:
        return

    running = is_running(bot_id)
    language = context.user_data.get("language", "fa")

    status = (
        "🟢 روشن" if running else "🔴 خاموش"
    ) if language == "fa" else (
        "🟢 Running" if running else "🔴 Stopped"
    )

    text = (
        f"🤖 نام ربات: {bot['name']}\n"
        f"وضعیت: {status}\n\n"
        f"{'✅' if success else '❌'} {message}"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=bot_control_keyboard(
            bot_id,
            running,
            language
        )
    )


async def bot_manager_noop(update, context):
    await update.callback_query.answer()
