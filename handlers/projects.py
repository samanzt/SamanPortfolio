
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes

from database.projects import get_active_projects, get_project
from database.stats import track_event
from keyboards.projects import projects_keyboard



async def show_projects(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    track_event(update.effective_user, "projects_list")

    language = context.user_data.get("language", "fa")
    projects = get_active_projects()

    if not projects:
        message = (
            "هنوز پروژه‌ای برای نمایش ثبت نشده است."
            if language == "fa"
            else "No projects have been added yet."
        )

        await update.message.reply_text(message)
        return

    message = (
        "📂 پروژه‌های من:\n\nیک پروژه را انتخاب کن:"
        if language == "fa"
        else "📂 My Projects:\n\nChoose a project:"
    )

    await update.message.reply_text(
        message,
        reply_markup=projects_keyboard(projects, language)
    )


async def show_project_details(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    project_id = int(query.data.split("_")[1])
    project = get_project(project_id)

    if project is None:
        message = (
            "این پروژه دیگر در دسترس نیست."
            if context.user_data.get("language", "fa") == "fa"
            else "This project is no longer available."
        )

        await query.edit_message_text(message)
        return

    track_event(
        update.effective_user,
        "project_details",
        project_id
    )

    language = context.user_data.get("language", "fa")

    if language == "fa":
        name = project["name_fa"]
        description = project["description_fa"]
        github_text = "مشاهده کد در GitHub"
        bot_text = "خودت امتحان کن"
    else:
        name = project["name_en"]
        description = project["description_en"]
        github_text = "View on GitHub"
        bot_text = "Try it yourself"

    message = f"🤖 {name}\n\n{description}"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                github_text,
                callback_data=f"github_click_{project_id}"
            )
        ],
        [
            InlineKeyboardButton(
                bot_text,
                callback_data=f"bot_click_{project_id}"
            )
        ]
    ])

    await query.edit_message_text(
        message,
        reply_markup=keyboard
    )


async def track_project_link_click(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    action = query.data.split("_")[0]
    project_id = int(query.data.rsplit("_", 1)[1])

    project = get_project(project_id)

    if project is None:
        message = (
            "این پروژه دیگر در دسترس نیست."
            if context.user_data.get("language", "fa") == "fa"
            else "This project is no longer available."
        )

        await query.message.reply_text(message)
        return

    language = context.user_data.get("language", "fa")

    if action == "github":
        track_event(
            update.effective_user,
            "github_click",
            project_id
        )

        url = project["github_url"]

        message = (
            "🐙 برای مشاهده کد پروژه روی دکمه زیر بزن:"
            if language == "fa"
            else "🐙 Open the project source code:"
        )

        button_text = (
            "باز کردن GitHub"
            if language == "fa"
            else "Open GitHub"
        )

    elif action == "bot":
        track_event(
            update.effective_user,
            "bot_click",
            project_id
        )

        url = project["bot_url"]

        message = (
            "🤖 برای اجرای ربات روی دکمه زیر بزن:"
            if language == "fa"
            else "🤖 Open the Telegram bot:"
        )

        button_text = (
            "باز کردن ربات"
            if language == "fa"
            else "Open Bot"
        )

    else:
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                button_text,
                url=url
            )
        ]
    ])

    await query.message.reply_text(
        message,
        reply_markup=keyboard
    )
