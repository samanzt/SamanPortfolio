from telegram import Update
from telegram.ext import ContextTypes,ConversationHandler
from config import ADMIN_ID
from keyboards.admin import admin_keyboard,delete_confirmation_keyboard
from urllib.parse import urlparse
from database.projects import add_project,get_active_projects,get_project,update_project
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from keyboards.admin import delete_projects_keyboard,edit_projects_keyboard,edit_fields_keyboard
from database.stats import get_statistics



(
    ADD_NAME_FA,
    ADD_NAME_EN,
    ADD_DESCRIPTION_FA,
    ADD_DESCRIPTION_EN,
    ADD_GITHUB,
    ADD_BOT_URL
) = range(6)

(
    EDIT_SELECT_PROJECT,
    EDIT_SELECT_FIELD,
    EDIT_WAIT_VALUE
) = range(10, 13)


async def admin_panel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.effective_message.reply_text(
            "⛔ شما اجازه دسترسی به پنل مدیریت را ندارید."
        )
        return

    await update.effective_message.reply_text(
        "🔐 پنل مدیریت\n\n"
        "عملیات موردنظر خود را انتخاب کن:",
        reply_markup=admin_keyboard()
    )



async def admin_menu_action(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer(
            "⛔ دسترسی غیرمجاز!",
            show_alert=True
        )
        return

    await query.answer()

    stats = get_statistics()
    language = context.user_data.get("language", "fa")

    if language == "fa":
        message = (
            "📊 آمار ربات\n\n"
            f"👥 کاربران یکتا: {stats['unique_users']}\n"
            f"🚀 دفعات اجرای start: {stats['start_count']}\n"
            f"📂 مشاهده فهرست پروژه‌ها: {stats['projects_list_views']}\n"
            f"🔎 مشاهده جزئیات پروژه‌ها: {stats['project_details_views']}\n"
            f"🐙 فشردن دکمه GitHub: {stats['github_clicks']}\n"
            f"🤖 فشردن دکمه ربات: {stats['bot_clicks']}"
        )
    else:
        message = (
            "📊 Bot Statistics\n\n"
            f"👥 Unique Users: {stats['unique_users']}\n"
            f"🚀 start Executions: {stats['start_count']}\n"
            f"📂 Project List Views: {stats['projects_list_views']}\n"
            f"🔎 Project Details Views: {stats['project_details_views']}\n"
            f"🐙 GitHub Button Clicks: {stats['github_clicks']}\n"
            f"🤖 Bot Button Clicks: {stats['bot_clicks']}"
        )

    await query.message.reply_text(message)



async def start_add_project(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
        return ConversationHandler.END

    await query.answer()

    context.user_data["new_project"] = {}

    await query.message.reply_text(
        "➕ افزودن پروژه جدید\n\n"
        "لطفاً نام فارسی پروژه را وارد کن:",
        reply_markup=cancel_keyboard()
    )

    return ADD_NAME_FA


async def receive_project_name_fa(update, context):
    name = update.message.text.strip()

    if not name:
        await update.message.reply_text(
            "❌ نام پروژه نمی‌تواند خالی باشد. دوباره وارد کن:"
        )
        return ADD_NAME_FA

    context.user_data["new_project"]["name_fa"] = name

    await update.message.reply_text(
        "نام انگلیسی پروژه را وارد کن:"
    )

    return ADD_NAME_EN


async def receive_project_name_en(update, context):
    name = update.message.text.strip()

    if not name:
        await update.message.reply_text(
            "❌ Project name cannot be empty. Try again:"
        )
        return ADD_NAME_EN

    context.user_data["new_project"]["name_en"] = name

    await update.message.reply_text(
        "توضیحات فارسی پروژه را وارد کن:"
    )

    return ADD_DESCRIPTION_FA


async def receive_project_description_fa(update, context):
    description = update.message.text.strip()

    if not description:
        await update.message.reply_text(
            "❌ توضیحات نمی‌تواند خالی باشد. دوباره وارد کن:"
        )
        return ADD_DESCRIPTION_FA

    context.user_data["new_project"]["description_fa"] = description

    await update.message.reply_text(
        "توضیحات انگلیسی پروژه را وارد کن:"
    )

    return ADD_DESCRIPTION_EN


async def receive_project_description_en(update, context):
    description = update.message.text.strip()

    if not description:
        await update.message.reply_text(
            "❌ Description cannot be empty. Try again:"
        )
        return ADD_DESCRIPTION_EN

    context.user_data["new_project"]["description_en"] = description

    await update.message.reply_text(
        "لینک مخزن GitHub پروژه را وارد کن:"
    )

    return ADD_GITHUB

async def receive_project_github(update, context):
    url = update.message.text.strip()
    parsed_url = urlparse(url)

    if (
        parsed_url.scheme != "https"
        or parsed_url.netloc != "github.com"
        or not parsed_url.path.strip("/")
    ):
        await update.message.reply_text(
            "❌ لینک GitHub معتبر نیست.\n"
            "لطفاً لینک صحیح مخزن را وارد کن:"
        )
        return ADD_GITHUB

    context.user_data["new_project"]["github_url"] = url

    await update.message.reply_text(
        "لینک ربات تلگرام پروژه را وارد کن:\n"
        "مثال: https://t.me/example_bot"
    )

    return ADD_BOT_URL


async def receive_project_bot_url(update, context):
    url = update.message.text.strip()
    parsed_url = urlparse(url)

    if (
        parsed_url.scheme != "https"
        or parsed_url.netloc != "t.me"
        or not parsed_url.path.strip("/")
    ):
        await update.message.reply_text(
            "❌ لینک ربات معتبر نیست.\n"
            "لطفاً لینکی مانند https://t.me/example_bot وارد کن:"
        )
        return ADD_BOT_URL

    context.user_data["new_project"]["bot_url"] = url

    data = context.user_data["new_project"]

    add_project(
        name_fa=data["name_fa"],
        name_en=data["name_en"],
        description_fa=data["description_fa"],
        description_en=data["description_en"],
        github_url=data["github_url"],
        bot_url=data["bot_url"]
    )

    context.user_data.pop("new_project", None)

    await update.message.reply_text(
        "✅ پروژه با موفقیت به دیتابیس اضافه شد!"
    )

    return ConversationHandler.END


async def cancel_add_project(update, context):
    context.user_data.pop("new_project", None)

    await update.message.reply_text(
        "❌ عملیات افزودن پروژه لغو شد.",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def cancel_keyboard():
    return ReplyKeyboardMarkup(
        [["❌ لغو عملیات"]],
        resize_keyboard=True,
        one_time_keyboard=False
    )


async def start_delete_project(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
        return

    await query.answer()

    language = context.user_data.get("language", "fa")
    projects = get_active_projects()

    if not projects:
        message = (
            "هیچ پروژه‌ای برای حذف وجود ندارد."
            if language == "fa"
            else "There are no projects to delete."
        )
        await query.message.reply_text(message)
        return

    message = (
        "🗑 پروژه موردنظر برای حذف را انتخاب کن:"
        if language == "fa"
        else "🗑 Select the project you want to delete:"
    )

    await query.message.reply_text(
        message,
        reply_markup=delete_projects_keyboard(projects, language)
    )


async def select_project_for_deletion(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
        return

    await query.answer()

    project_id = int(query.data.split("_")[-1])
    project = get_project(project_id)

    language = context.user_data.get("language", "fa")

    if project is None:
        await query.edit_message_text(
            "این پروژه دیگر در دسترس نیست."
            if language == "fa"
            else "This project is no longer available."
        )
        return

    name = (
        project["name_fa"]
        if language == "fa"
        else project["name_en"]
    )

    await query.edit_message_text(
        (
            f"⚠️ آیا مطمئنی می‌خواهی پروژه «{name}» را حذف کنی؟"
            if language == "fa"
            else f"⚠️ Are you sure you want to delete '{name}'?"
        ),
        reply_markup=delete_confirmation_keyboard(project_id, language)
    )


async def cancel_delete_project(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
        return

    await query.answer()

    language = context.user_data.get("language", "fa")

    await query.edit_message_text(
        "❌ عملیات حذف لغو شد."
        if language == "fa"
        else "❌ Deletion cancelled."
    )


async def confirm_delete_project(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
        return

    await query.answer()

    project_id = int(query.data.split("_")[-1])
    language = context.user_data.get("language", "fa")

    from database.projects import delete_project

    success = delete_project(project_id)

    if success:
        message = (
            "✅ پروژه با موفقیت حذف شد."
            if language == "fa"
            else "✅ Project deleted successfully."
        )
    else:
        message = (
            "❌ حذف پروژه انجام نشد."
            if language == "fa"
            else "❌ Failed to delete project."
        )

    await query.edit_message_text(message)


async def start_edit_project(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
        return ConversationHandler.END

    await query.answer()

    language = context.user_data.get("language", "fa")
    projects = get_active_projects()

    if not projects:
        await query.message.reply_text("هیچ پروژه‌ای برای ویرایش وجود ندارد.")
        return ConversationHandler.END

    await query.message.reply_text(
        "✏️ پروژه موردنظر را انتخاب کن:",
        reply_markup=edit_projects_keyboard(projects, language)
    )

    return EDIT_SELECT_PROJECT


async def select_project_for_edit(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
        return ConversationHandler.END

    await query.answer()

    project_id = int(query.data.split("_")[-1])
    project = get_project(project_id)

    if project is None:
        await query.edit_message_text("❌ پروژه پیدا نشد.")
        return ConversationHandler.END

    context.user_data["editing_project_id"] = project_id

    language = context.user_data.get("language", "fa")

    if language == "fa":
        message = (
            f"✏️ ویرایش پروژه: {project['name_fa']}\n\n"
            f"نام فارسی: {project['name_fa']}\n"
            f"نام انگلیسی: {project['name_en']}\n"
            f"توضیحات فارسی: {project['description_fa']}\n"
            f"توضیحات انگلیسی: {project['description_en']}\n"
            f"GitHub: {project['github_url']}\n"
            f"Bot: {project['bot_url']}\n\n"
            "کدام قسمت را می‌خواهی تغییر بدهی؟"
        )
    else:
        message = (
            f"✏️ Edit Project: {project['name_en']}\n\n"
            f"Persian Name: {project['name_fa']}\n"
            f"English Name: {project['name_en']}\n"
            f"Persian Description: {project['description_fa']}\n"
            f"English Description: {project['description_en']}\n"
            f"GitHub: {project['github_url']}\n"
            f"Bot: {project['bot_url']}\n\n"
            "Which field do you want to edit?"
        )

    await query.edit_message_text(
        message,
        reply_markup=edit_fields_keyboard(project_id, language)
    )

    return EDIT_SELECT_FIELD


async def select_edit_field(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
        return ConversationHandler.END

    await query.answer()

    field = query.data.replace("edit_field_", "")

    allowed_fields = {
        "name_fa": "نام فارسی",
        "name_en": "نام انگلیسی",
        "description_fa": "توضیحات فارسی",
        "description_en": "توضیحات انگلیسی",
        "github_url": "لینک GitHub",
        "bot_url": "لینک ربات"
    }

    if field not in allowed_fields:
        return EDIT_SELECT_FIELD

    context.user_data["editing_field"] = field

    title = allowed_fields[field]

    await query.message.reply_text(
        f"مقدار جدید {title} را وارد کن:"
    )

    return EDIT_WAIT_VALUE


from urllib.parse import urlparse


async def receive_edit_value(update, context):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    value = update.message.text.strip()

    if not value:
        await update.message.reply_text("❌ مقدار نمی‌تواند خالی باشد.")
        return EDIT_WAIT_VALUE

    field = context.user_data["editing_field"]

    if field == "github_url":
        parsed = urlparse(value)

        if (
            parsed.scheme != "https"
            or parsed.netloc != "github.com"
            or not parsed.path.strip("/")
        ):
            await update.message.reply_text("❌ لینک GitHub معتبر نیست.")
            return EDIT_WAIT_VALUE

    elif field == "bot_url":
        parsed = urlparse(value)

        if (
            parsed.scheme != "https"
            or parsed.netloc != "t.me"
            or not parsed.path.strip("/")
        ):
            await update.message.reply_text("❌ لینک ربات معتبر نیست.")
            return EDIT_WAIT_VALUE

    project_id = context.user_data["editing_project_id"]
    project = get_project(project_id)

    if project is None:
        await update.message.reply_text("❌ پروژه پیدا نشد.")
        return ConversationHandler.END

    data = dict(project)
    data[field] = value

    success = update_project(
        project_id=project_id,
        name_fa=data["name_fa"],
        name_en=data["name_en"],
        description_fa=data["description_fa"],
        description_en=data["description_en"],
        github_url=data["github_url"],
        bot_url=data["bot_url"]
    )

    context.user_data.pop("editing_field", None)

    if success:
        await update.message.reply_text(
            "✅ اطلاعات پروژه با موفقیت ویرایش شد."
        )
    else:
        await update.message.reply_text(
            "❌ ویرایش پروژه ناموفق بود."
        )

    context.user_data.pop("editing_project_id", None)

    return ConversationHandler.END


