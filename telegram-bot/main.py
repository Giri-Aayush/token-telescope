import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from handlers.bot_handlers import start, button, get_address, get_sender, get_subscription_address
from handlers.commands import help_command, watchlist_command, subscription_command
from database import SupabaseDB
from constants import WAITING_FOR_ADDRESS, WAITING_FOR_SENDER, WAITING_FOR_SUBSCRIPTION_ADDRESS

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    load_dotenv()
    
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "TELEGRAM_TOKEN"]
    env_vars = {var: os.getenv(var) for var in required_vars}
    
    if not all(env_vars.values()):
        missing = [var for var, val in env_vars.items() if not val]
        logger.error(f"Missing environment variables: {missing}")
        return

    supabase = SupabaseDB(url=env_vars["SUPABASE_URL"], key=env_vars["SUPABASE_KEY"])
    application = Application.builder().token(env_vars["TELEGRAM_TOKEN"]).build()
    application.bot_data["supabase"] = supabase

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
        states={
            WAITING_FOR_ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_address),
                CallbackQueryHandler(button, pattern="main_menu|confirm_predict_.*")
            ],
            WAITING_FOR_SENDER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_sender),
                CallbackQueryHandler(button, pattern="main_menu|confirm_monitor_.*")
            ],
            WAITING_FOR_SUBSCRIPTION_ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_subscription_address),
                CallbackQueryHandler(button, pattern="main_menu|confirm_subscribe_.*")
            ],
        },
        fallbacks=[],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("watchlist", watchlist_command))
    application.add_handler(CommandHandler("subscription", subscription_command))

    logger.info("Bot started and polling...")
    application.run_polling()

if __name__ == "__main__":
    main()