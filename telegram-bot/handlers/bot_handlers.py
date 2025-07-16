from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from web3 import Web3
from datetime import datetime, timedelta
import logging

from utils import predict_contract_address, is_subscribed, validate_eth_address
from constants import (WAITING_FOR_ADDRESS, WAITING_FOR_SENDER, 
                      WAITING_FOR_SUBSCRIPTION_ADDRESS, Messages, TransactionState)
from keyboards import KeyboardFactory
from config import config
from transaction_monitor import TransactionMonitor
from database import SupabaseDB

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    supabase: SupabaseDB = context.bot_data["supabase"]
    user = update.effective_user
    
    supabase.add_user(telegram_id=user.id, username=user.username or "unknown")
    subscription = supabase.get_subscription(telegram_id=user.id)
    network_indicator = config.get_network_indicator()
    
    if is_subscribed(subscription):
        keyboard = KeyboardFactory.main_menu_subscribed(network_indicator)
        text = Messages.WELCOME_SUBSCRIBED.format(user.first_name or user.username)
        logger.info(f"User {user.id} (subscribed) started the bot")
    else:
        keyboard = KeyboardFactory.main_menu_unsubscribed(network_indicator)
        text = Messages.WELCOME_UNSUBSCRIBED
        logger.info(f"User {user.id} (not subscribed) started the bot")
    
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    supabase: SupabaseDB = context.bot_data["supabase"]
    user_id = query.from_user.id
    data = query.data
    
    logger.info(f"Button callback: user_id={user_id}, data={data}")
    
    subscription = supabase.get_subscription(telegram_id=user_id)
    network_indicator = config.get_network_indicator()
    
    if data == "main_menu":
        return await _handle_main_menu(query, subscription, network_indicator)
    
    if data == "toggle_network":
        return await _handle_network_toggle(query, subscription)
    
    if not is_subscribed(subscription) and data not in ["subscribe", "help"] and not data.startswith("confirm_subscribe_"):
        await query.edit_message_text(
            Messages.SUBSCRIPTION_REQUIRED,
            reply_markup=KeyboardFactory.subscription_required(),
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    
    return await _handle_button_actions(query, context, data, supabase, user_id)

async def _handle_main_menu(query, subscription, network_indicator):
    if is_subscribed(subscription):
        keyboard = KeyboardFactory.main_menu_subscribed(network_indicator)
        text = Messages.WELCOME_SUBSCRIBED.format(query.from_user.first_name or query.from_user.username)
    else:
        keyboard = KeyboardFactory.main_menu_unsubscribed(network_indicator)
        text = Messages.WELCOME_UNSUBSCRIBED
    
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
    return ConversationHandler.END

async def _handle_network_toggle(query, subscription):
    new_network = config.toggle_network()
    network_indicator = config.get_network_indicator()
    
    if is_subscribed(subscription):
        keyboard = KeyboardFactory.main_menu_subscribed(network_indicator)
        text = Messages.WELCOME_SUBSCRIBED.format(query.from_user.first_name or query.from_user.username)
    else:
        keyboard = KeyboardFactory.main_menu_unsubscribed(network_indicator)
        text = Messages.WELCOME_UNSUBSCRIBED
    
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
    logger.info(f"User {query.from_user.id} toggled network to {new_network}")
    return ConversationHandler.END

async def _handle_button_actions(query, context, data, supabase, user_id):
    if data == "subscribe":
        return await _handle_subscribe(query, context)
    elif data == "predict":
        return await _handle_predict(query)
    elif data == "monitor":
        return await _handle_monitor(query)
    elif data == "watchlist":
        return await _handle_watchlist(query, supabase, user_id)
    elif data.startswith("delete_"):
        return await _handle_delete_entry(query, supabase, user_id, data)
    elif data == "help":
        return await _handle_help(query)
    elif data.startswith("confirm_predict_"):
        return await _handle_confirm_predict(query, supabase, user_id, data)
    elif data.startswith("confirm_monitor_"):
        return await _handle_confirm_monitor(query, context, user_id, data)
    elif data.startswith("confirm_subscribe_"):
        return await _handle_confirm_subscribe(query, context, supabase, user_id, data)
    
    return ConversationHandler.END

async def _handle_subscribe(query, context):
    try:
        await query.edit_message_text(
            "💎 *Subscribe to Contract Predictor Bot*\n\n"
            f"Please send the sender address (0x...) to initiate a payment of 0.01 ETH to `{config.RECIPIENT_ADDRESS}`.\n"
            "⚠️ *Do not close this window* until payment confirmation is received.\n"
            f"Monitoring will timeout after {config.MAX_BLOCKS_TO_WAIT} blocks (~{config.MAX_BLOCKS_TO_WAIT * 12 // 60} minutes).",
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.cancel_action()
        )
        return WAITING_FOR_SUBSCRIPTION_ADDRESS
    except Exception as e:
        logger.error(f"Error in subscribe flow: {e}")
        await query.edit_message_text(
            "❌ *Error*: An unexpected error occurred. Please try again or contact support.",
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.retry_or_back("subscribe")
        )
        return ConversationHandler.END

async def _handle_predict(query):
    await query.edit_message_text(
        "🔮 *Predict Contract Address*\n\n"
        "Please send the sender address (0x...):",
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.back_to_main()
    )
    return WAITING_FOR_ADDRESS

async def _handle_monitor(query):
    await query.edit_message_text(
        "💸 *Monitor Payment*\n\n"
        "Please send the sender address (0x...) to monitor for payments:",
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.back_to_main()
    )
    return WAITING_FOR_SENDER

async def _handle_watchlist(query, supabase, user_id):
    watchlist = supabase.get_watchlist(telegram_id=user_id)
    if not watchlist:
        await query.edit_message_text(
            "📋 *Your Watchlist*\n\n"
            "No addresses in your watchlist yet.",
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.back_to_main()
        )
        return ConversationHandler.END

    response = "📋 *Your Watchlist*\n\n"
    for entry in watchlist:
        response += (
            f"🔹 *Entry {entry['id']}*\n"
            f"  • Sender: `{entry['sender_address']}`\n"
            f"  • Nonce: `{entry['nonce']}`\n"
            f"  • Predicted: `{entry['predicted_address']}`\n"
            f"  • Added: `{entry['created_at']}`\n\n"
        )
    
    keyboard = KeyboardFactory.watchlist_actions(watchlist)
    await query.edit_message_text(response, reply_markup=keyboard, parse_mode="Markdown")
    return ConversationHandler.END

async def _handle_delete_entry(query, supabase, user_id, data):
    entry_id = int(data.split("_")[1])
    success = supabase.delete_watchlist_entry(entry_id=entry_id, telegram_id=user_id)
    text = "✅ *Entry deleted successfully!*" if success else "❌ *Failed to delete entry.*"
    
    await query.edit_message_text(
        f"{text}\n\nSelect an option to continue:",
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.retry_or_back("watchlist")
    )
    return ConversationHandler.END

async def _handle_help(query):
    await query.edit_message_text(
        Messages.HELP_TEXT,
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.back_to_main()
    )
    return ConversationHandler.END

async def _handle_confirm_predict(query, supabase, user_id, data):
    sender = data.split("confirm_predict_")[1]
    try:
        web3 = Web3(Web3.HTTPProvider(config.rpc_url))
        nonce = web3.eth.get_transaction_count(web3.to_checksum_address(sender))
        address = predict_contract_address(sender, nonce)
        
        added = supabase.add_watchlist_entry(
            telegram_id=user_id,
            sender_address=sender,
            nonce=nonce,
            predicted_address=address
        )
        
        message = (
            f"✅ *Prediction Complete!*\n\n"
            f"• Sender: `{sender}`\n"
            f"• Nonce: `{nonce}`\n"
            f"• Predicted: `{address}`\n\n"
            f"{'Added to your watchlist!' if added else 'Already in your watchlist!'}"
        )
        
        await query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.retry_or_back("watchlist")
        )
    except Exception as e:
        logger.error(f"Error in predict confirmation: {e}")
        await query.edit_message_text(
            f"❌ *Error*: {e}\n\nTry again or return to the main menu.",
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.back_to_main()
        )
    return ConversationHandler.END

async def _handle_confirm_monitor(query, context, user_id, data):
    sender = data.split("confirm_monitor_")[1]
    try:
        monitor = TransactionMonitor(config.rpc_url)
        context.bot_data["monitor"] = monitor
        
        await query.edit_message_text(
            f"🔍 *Monitoring Payment*\n\n"
            f"Monitoring transactions from `{sender}` to `{config.RECIPIENT_ADDRESS}`.\n"
            f"Expected amount: `{config.EXPECTED_AMOUNT} ETH`.\n"
            f"Will monitor for {config.MAX_BLOCKS_TO_WAIT} blocks (~{config.MAX_BLOCKS_TO_WAIT * 12 // 60} minutes).\n\n"
            f"⚠️ *Do not close this window* until confirmation is received.",
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.cancel_action()
        )
        
        result = await monitor.monitor_transaction(sender)
        await monitor.destroy()
        del context.bot_data["monitor"]
        
        message = _format_monitor_result(result, monitor)
        await query.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.retry_or_back("monitor")
        )
    except Exception as e:
        logger.error(f"Error in monitor confirmation: {e}")
        await query.edit_message_text(
            f"❌ *Error*: {e}",
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.back_to_main()
        )
        if "monitor" in context.bot_data:
            await context.bot_data["monitor"].destroy()
            del context.bot_data["monitor"]
    return ConversationHandler.END

async def _handle_confirm_subscribe(query, context, supabase, user_id, data):
    sender = data.split("confirm_subscribe_")[1]
    try:
        monitor = TransactionMonitor(config.rpc_url)
        context.bot_data["monitor"] = monitor
        
        await query.edit_message_text(
            f"🔍 *Monitoring Subscription Payment*\n\n"
            f"Monitoring transactions from `{sender}` to `{config.RECIPIENT_ADDRESS}`.\n"
            "Expected amount: `0.01 ETH`.\n"
            f"Will monitor for {config.MAX_BLOCKS_TO_WAIT} blocks (~{config.MAX_BLOCKS_TO_WAIT * 12 // 60} minutes).\n\n"
            f"⚠️ *Do not close this window* until confirmation is received.",
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.cancel_action()
        )
        
        result = await monitor.monitor_transaction(sender)
        await monitor.destroy()
        del context.bot_data["monitor"]
        
        if result == TransactionState.FOUND_CORRECT_AMOUNT:
            expiry_date = (datetime.now() + timedelta(days=30)).isoformat()
            
            if not supabase.get_subscription(telegram_id=user_id):
                supabase.add_subscription(telegram_id=user_id, recipient_address=config.RECIPIENT_ADDRESS)
            
            supabase.update_subscription(telegram_id=user_id, is_active=True, expiry_date=expiry_date)
            
            message = (
                f"✅ *Subscription Activated!*\n\n"
                "You now have full access to all features for 30 days!\n"
                f"Expiry: `{expiry_date}`\n\n"
                "Use /start to access the main menu."
            )
        else:
            message = _format_monitor_result(result, monitor)
        
        await query.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.retry_or_back("subscribe")
        )
    except Exception as e:
        logger.error(f"Error in confirm_subscribe: {e}")
        await query.edit_message_text(
            f"❌ *Error*: {e}",
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.retry_or_back("subscribe")
        )
        if "monitor" in context.bot_data:
            await context.bot_data["monitor"].destroy()
            del context.bot_data["monitor"]
    return ConversationHandler.END

def _format_monitor_result(result: TransactionState, monitor: TransactionMonitor) -> str:
    if result == TransactionState.FOUND_CORRECT_AMOUNT:
        return (
            f"✅ *Payment Confirmed!*\n\n"
            f"Expected amount of `{config.EXPECTED_AMOUNT} ETH` or more received."
        )
    elif result == TransactionState.FOUND_INCORRECT_AMOUNT:
        message = (
            f"⚠️ *Incorrect Payment Amount!*\n\n"
            f"Found transactions, but none met the expected amount of `{config.EXPECTED_AMOUNT} ETH`.\n"
            f"Details:\n"
        )
        for tx in monitor.found_transactions:
            message += f"• Hash: `{tx['hash']}`\n  Amount: `{tx['amount']} ETH`\n"
        return message
    elif result == TransactionState.TIMEOUT:
        return (
            f"⏰ *Monitoring Timeout!*\n\n"
            f"No matching transactions found within {config.MAX_BLOCKS_TO_WAIT} blocks.\n"
            "If you have paid, please contact support."
        )
    else:
        return "❓ *Unexpected Result*\n\nPlease try again or contact support."

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sender = update.message.text.strip()
    
    if not validate_eth_address(sender):
        await update.message.reply_text(
            Messages.INVALID_ADDRESS,
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.retry_or_back("predict")
        )
        return WAITING_FOR_ADDRESS

    await update.message.reply_text(
        f"🔮 *Confirm Sender Address*\n\n"
        f"You entered: `{sender}`\n"
        "Is this correct?",
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.confirm_action("predict", sender)
    )
    return WAITING_FOR_ADDRESS

async def get_sender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sender = update.message.text.strip()
    
    if not validate_eth_address(sender):
        await update.message.reply_text(
            Messages.INVALID_ADDRESS,
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.retry_or_back("monitor")
        )
        return WAITING_FOR_SENDER

    await update.message.reply_text(
        f"💸 *Confirm Sender Address*\n\n"
        f"You entered: `{sender}`\n"
        "Is this correct?",
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.confirm_action("monitor", sender)
    )
    return WAITING_FOR_SENDER

async def get_subscription_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sender = update.message.text.strip()
    
    if not validate_eth_address(sender):
        await update.message.reply_text(
            Messages.INVALID_ADDRESS,
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.retry_or_back("subscribe")
        )
        return WAITING_FOR_SUBSCRIPTION_ADDRESS

    await update.message.reply_text(
        f"💎 *Confirm Subscription Payment*\n\n"
        f"Sender: `{sender}`\n"
        f"Recipient: `{config.RECIPIENT_ADDRESS}`\n"
        "Amount: `0.01 ETH`\n"
        f"Timeout: ~{config.MAX_BLOCKS_TO_WAIT * 12 // 60} minutes\n\n"
        "Is this correct? Confirm to start monitoring.",
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.confirm_action("subscribe", sender)
    )
    return WAITING_FOR_SUBSCRIPTION_ADDRESS