
import logging

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler
)

from config import BOT_TOKEN

from database.projects import init_db
from database.stats import init_stats_db
from database.bots import init_bots_db

from handlers.start import start
from handlers.error import error_handler
from handlers.language import select_language
from handlers.about import show_about
from handlers.skills import show_skills
from handlers.contact import show_contact

from handlers.admin import (
    admin_panel,
    admin_menu_action,
    start_add_project,
    receive_project_name_fa,
    receive_project_name_en,
    receive_project_description_fa,
    receive_project_description_en,
    receive_project_github,
    receive_project_bot_url,
    cancel_add_project,
    ADD_NAME_FA,
    ADD_NAME_EN,
    ADD_DESCRIPTION_FA,
    ADD_DESCRIPTION_EN,
    ADD_GITHUB,
    ADD_BOT_URL,
    start_delete_project,
    select_project_for_deletion,
    cancel_delete_project,
    confirm_delete_project,
    start_edit_project,
    EDIT_SELECT_PROJECT,
    EDIT_SELECT_FIELD,
    EDIT_WAIT_VALUE,
    select_project_for_edit,
    select_edit_field,
    receive_edit_value
)

from handlers.projects import (
    show_projects,
    show_project_details,
    track_project_link_click
)

from handlers.bot_manager.handlers import (
    open_bot_manager,
    show_managed_bots,
    select_managed_bot,
    back_to_admin,
    start_add_bot,
    receive_bot_name,
    receive_bot_username,
    receive_bot_project_path,
    receive_bot_venv_path,
    receive_bot_entry_file,
    cancel_add_bot,
    manage_bot_action,
    bot_manager_noop,
    BOT_NAME,
    BOT_USERNAME,
    BOT_PROJECT_PATH,
    BOT_VENV_PATH,
    BOT_ENTRY_FILE
)
from handlers.resume import send_resume


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


def main():

    # Initialize databases
    init_db()
    init_stats_db()
    init_bots_db()

    print("Database initialized successfully.")

    app = Application.builder().token(BOT_TOKEN).build()

    # -------------------------
    # Basic handlers
    # -------------------------

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(
            select_language,
            pattern="^lang_(fa|en)$"
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^(درباره من|About Me)$"),
            show_about
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^(مهارت‌ها|Skills)$"),
            show_skills
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^(اطلاعات تماس|Contact)$"),
            show_contact
        )
    )
    app.add_handler(
        MessageHandler(
            filters.Regex("^(دریافت رزومه|Download Resume)$"),
            send_resume
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^(پروژه‌ها|Projects)$"),
            show_projects
        )
    )

    # -------------------------
    # Admin handlers
    # -------------------------

    app.add_handler(
        CommandHandler("admin", admin_panel)
    )

    app.add_handler(
        CallbackQueryHandler(
            admin_menu_action,
            pattern="^admin_stats$"
        )
    )

    # -------------------------
    # Add project conversation
    # -------------------------

    add_project_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                start_add_project,
                pattern="^admin_add$"
            )
        ],
        states={
            ADD_NAME_FA: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_project_name_fa
                )
            ],
            ADD_NAME_EN: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_project_name_en
                )
            ],
            ADD_DESCRIPTION_FA: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_project_description_fa
                )
            ],
            ADD_DESCRIPTION_EN: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_project_description_en
                )
            ],
            ADD_GITHUB: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_project_github
                )
            ],
            ADD_BOT_URL: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_project_bot_url
                )
            ]
        },
        fallbacks=[
            MessageHandler(
                filters.Regex("^❌ لغو عملیات$"),
                cancel_add_project
            )
        ]
    )

    app.add_handler(add_project_conversation)

    # -------------------------
    # Project handlers
    # -------------------------

    app.add_handler(
        CallbackQueryHandler(
            show_project_details,
            pattern=r"^project_\d+$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            track_project_link_click,
            pattern=r"^(github|bot)_click_\d+$"
        )
    )

    # -------------------------
    # Delete project handlers
    # -------------------------

    app.add_handler(
        CallbackQueryHandler(
            start_delete_project,
            pattern="^admin_delete$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            select_project_for_deletion,
            pattern=r"^delete_select_\d+$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            cancel_delete_project,
            pattern=r"^delete_cancel$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            confirm_delete_project,
            pattern=r"^delete_confirm_\d+$"
        )
    )

    # -------------------------
    # Edit project conversation
    # -------------------------

    edit_project_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                start_edit_project,
                pattern="^admin_edit$"
            )
        ],
        states={
            EDIT_SELECT_PROJECT: [
                CallbackQueryHandler(
                    select_project_for_edit,
                    pattern=r"^edit_select_\d+$"
                )
            ],
            EDIT_SELECT_FIELD: [
                CallbackQueryHandler(
                    select_edit_field,
                    pattern=(
                        r"^edit_field_"
                        r"(name_fa|name_en|description_fa|"
                        r"description_en|github_url|bot_url)$"
                    )
                )
            ],
            EDIT_WAIT_VALUE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_edit_value
                )
            ]
        },
        fallbacks=[]
    )

    app.add_handler(edit_project_conversation)

    # -------------------------
    # Add bot conversation
    # -------------------------

    add_bot_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                start_add_bot,
                pattern="^bm_add$"
            )
        ],
        states={
            BOT_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_bot_name
                )
            ],
            BOT_USERNAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_bot_username
                )
            ],
            BOT_PROJECT_PATH: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_bot_project_path
                )
            ],
            BOT_VENV_PATH: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_bot_venv_path
                )
            ],
            BOT_ENTRY_FILE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_bot_entry_file
                )
            ]
        },
        fallbacks=[
            CommandHandler(
                "cancel",
                cancel_add_bot
            )
        ]
    )

    app.add_handler(add_bot_conversation)

    # -------------------------
    # Bot manager handlers
    # -------------------------

    app.add_handler(
        CallbackQueryHandler(
            open_bot_manager,
            pattern="^admin_bot_manager$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            show_managed_bots,
            pattern="^bm_list$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            select_managed_bot,
            pattern=r"^bm_select_\d+$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            back_to_admin,
            pattern="^bm_back_admin$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            show_managed_bots,
            pattern="^bm_back_manager$"
        )
    )

    # Start / Stop / Restart
    app.add_handler(
        CallbackQueryHandler(
            manage_bot_action,
            pattern=r"^bm_(start|stop|restart)_\d+$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            bot_manager_noop,
            pattern="^bm_noop$"
        )
    )

    # -------------------------
    # Error handler
    # -------------------------

    app.add_error_handler(error_handler)

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
