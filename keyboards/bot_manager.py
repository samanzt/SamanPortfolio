
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def bot_manager_keyboard(language="fa"):
    if language == "fa":
        buttons = [
            ("➕ افزودن ربات", "bm_add"),
            ("🤖 ربات‌های من", "bm_list"),
            ("🔙 بازگشت به پنل ادمین", "bm_back_admin")
        ]
    else:
        buttons = [
            ("➕ Add Bot", "bm_add"),
            ("🤖 My Bots", "bm_list"),
            ("🔙 Back to Admin Panel", "bm_back_admin")
        ]

    keyboard = [
        [InlineKeyboardButton(text, callback_data=data)]
        for text, data in buttons
    ]

    return InlineKeyboardMarkup(keyboard)


def managed_bots_keyboard(bots, language="fa"):
    keyboard = []

    for bot in bots:
        name = bot["name"]

        keyboard.append([
            InlineKeyboardButton(
                f"🤖 {name}",
                callback_data=f"bm_select_{bot['id']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 بازگشت" if language == "fa" else "🔙 Back",
            callback_data="bm_back_manager"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


def bot_control_keyboard(bot_id, running, language="fa"):
    if language == "fa":
        start_text = "🟢 روشن کردن"
        stop_text = "🔴 خاموش کردن"
        restart_text = "🔄 راه‌اندازی مجدد"
        back_text = "🔙 بازگشت به لیست"
        status_text = "🟢 روشن" if running else "🔴 خاموش"
    else:
        start_text = "🟢 Start"
        stop_text = "🔴 Stop"
        restart_text = "🔄 Restart"
        back_text = "🔙 Back to List"
        status_text = "🟢 Running" if running else "🔴 Stopped"

    keyboard = [
        [InlineKeyboardButton(status_text, callback_data="bm_noop")],
        [
            InlineKeyboardButton(
                start_text,
                callback_data=f"bm_start_{bot_id}"
            )
        ],
        [
            InlineKeyboardButton(
                stop_text,
                callback_data=f"bm_stop_{bot_id}"
            )
        ],
        [
            InlineKeyboardButton(
                restart_text,
                callback_data=f"bm_restart_{bot_id}"
            )
        ],
        [
            InlineKeyboardButton(
                back_text,
                callback_data="bm_list"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)
