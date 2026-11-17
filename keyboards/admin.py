from telegram import InlineKeyboardButton, InlineKeyboardMarkup



def admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "➕ افزودن پروژه",
                callback_data="admin_add"
            )
        ],
        [
            InlineKeyboardButton(
                "✏️ ویرایش پروژه",
                callback_data="admin_edit"
            )
        ],
        [
            InlineKeyboardButton(
                "🗑 حذف پروژه",
                callback_data="admin_delete"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 آمار ربات",
                callback_data="admin_stats"
            )
        ],
        [
            InlineKeyboardButton(
                "🤖 مدیریت ربات‌ها",
                callback_data="admin_bot_manager"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def delete_projects_keyboard(projects, language="fa"):
    keyboard = []

    for project in projects:
        name = (
            project["name_fa"]
            if language == "fa"
            else project["name_en"]
        )

        keyboard.append([
            InlineKeyboardButton(
                f"🗑 {name}",
                callback_data=f"delete_select_{project['id']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "❌ لغو عملیات" if language == "fa" else "❌ Cancel",
            callback_data="delete_cancel"
        )
    ])

    return InlineKeyboardMarkup(keyboard)

def delete_confirmation_keyboard(project_id, language="fa"):
    if language == "fa":
        yes_text = "✅ بله، حذف کن"
        no_text = "❌ لغو"
    else:
        yes_text = "✅ Yes, delete"
        no_text = "❌ Cancel"

    keyboard = [
        [
            InlineKeyboardButton(
                yes_text,
                callback_data=f"delete_confirm_{project_id}"
            )
        ],
        [
            InlineKeyboardButton(
                no_text,
                callback_data="delete_cancel"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def edit_projects_keyboard(projects, language="fa"):
    keyboard = []

    for project in projects:
        name = (
            project["name_fa"]
            if language == "fa"
            else project["name_en"]
        )

        keyboard.append([
            InlineKeyboardButton(
                f"✏️ {name}",
                callback_data=f"edit_select_{project['id']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "❌ لغو عملیات" if language == "fa" else "❌ Cancel",
            callback_data="edit_cancel"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


def edit_fields_keyboard(project_id, language="fa"):
    fields = {
        "name_fa": "نام فارسی",
        "name_en": "نام انگلیسی",
        "description_fa": "توضیحات فارسی",
        "description_en": "توضیحات انگلیسی",
        "github_url": "لینک GitHub",
        "bot_url": "لینک ربات"
    }

    keyboard = []

    for field, title in fields.items():
        if language == "en":
            titles = {
                "name_fa": "Persian Name",
                "name_en": "English Name",
                "description_fa": "Persian Description",
                "description_en": "English Description",
                "github_url": "GitHub Link",
                "bot_url": "Bot Link"
            }
            title = titles[field]

        keyboard.append([
            InlineKeyboardButton(
                f"✏️ {title}",
                callback_data=f"edit_field_{field}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 بازگشت" if language == "fa" else "🔙 Back",
            callback_data="edit_back"
        )
    ])
    return InlineKeyboardMarkup(keyboard)