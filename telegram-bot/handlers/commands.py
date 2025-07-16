from telegram import Update
from telegram.ext import ContextTypes
import logging

from utils import is_subscribed, format_watchlist_entry
from constants import Messages
from keyboards import KeyboardFactory
from database import SupabaseDB

logger = logging.getLogger(__name__)

async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    supabase: SupabaseDB = context.bot_data["supabase"]
    user_id = update.effective_user.id
    subscription = supabase.get_subscription(telegram_id=user_id)

    if not is_subscribed(subscription):
        await update.message.reply_text(
            Messages.SUBSCRIPTION_REQUIRED,
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.subscription_required()
        )
        logger.info(f"User {user_id} attempted watchlist without subscription")
        return

    watchlist = supabase.get_watchlist(telegram_id=user_id)
    if not watchlist:
        await update.message.reply_text(
            "📋 *Your Watchlist*\n\n"
            "No addresses in your watchlist yet.",
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.back_to_main()
        )
        logger.info(f"User {user_id} viewed empty watchlist")
        return

    response = "📋 *Your Watchlist*\n\n"
    for entry in watchlist:
        response += format_watchlist_entry(entry)
    
    keyboard = KeyboardFactory.watchlist_actions(watchlist)
    await update.message.reply_text(response, reply_markup=keyboard, parse_mode="Markdown")
    logger.info(f"User {user_id} viewed watchlist")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        Messages.HELP_TEXT,
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.back_to_main()
    )
    logger.info(f"User {update.effective_user.id} viewed help menu")

async def subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    supabase: SupabaseDB = context.bot_data["supabase"]
    subscription = supabase.get_subscription(telegram_id=update.effective_user.id)
    
    if is_subscribed(subscription):
        expiry_date = subscription.get("expiry_date", "N/A")
        text = (
            f"📝 *Subscription Status*\n\n"
            f"Status: *Active*\n"
            f"Expiry Date: `{expiry_date}`\n\n"
            "Use /start to access the main menu."
        )
        logger.info(f"User {update.effective_user.id} checked subscription: active, expires {expiry_date}")
    else:
        text = (
            "📝 *Subscription Status*\n\n"
            "Status: *Not Subscribed*\n\n"
            "Subscribe for just 0.01 ETH/month to unlock all features!\n"
            "Use the button below to subscribe or type /help for more info."
        )
        logger.info(f"User {update.effective_user.id} checked subscription: not subscribed")
    
    keyboard = (KeyboardFactory.back_to_main() if is_subscribed(subscription) 
               else KeyboardFactory.subscription_required())
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)