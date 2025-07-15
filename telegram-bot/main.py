# main.py
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from handler import start, button, get_address, get_sender, help_command, watchlist_command, subscription_command, get_subscription_address
from database import SupabaseDB

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_ADDRESS, WAITING_FOR_SENDER, WAITING_FOR_SUBSCRIPTION_ADDRESS = range(3)

def main() -> None:
    # Load environment variables
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    telegram_token = os.getenv("TELEGRAM_TOKEN")

    if not all([supabase_url, supabase_key, telegram_token]):
        logger.error("Missing environment variables")
        return

    # Initialize Supabase client
    supabase = SupabaseDB(url=supabase_url, key=supabase_key)

    # Initialize the Telegram bot application
    application = Application.builder().token(telegram_token).build()

    # Store Supabase client in bot_data
    application.bot_data["supabase"] = supabase

    # Define the conversation handler
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
    logger.debug("[DEBUG] Conversation handler initialized with states: WAITING_FOR_ADDRESS, WAITING_FOR_SENDER, WAITING_FOR_SUBSCRIPTION_ADDRESS")
    # Add handlers to the application
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("watchlist", watchlist_command))
    application.add_handler(CommandHandler("subscription", subscription_command))

    # Start the bot
    logger.info("Bot started and polling...")
    application.run_polling()

if __name__ == "__main__":
    main()