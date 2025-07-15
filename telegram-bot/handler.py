# handler.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from web3 import Web3
from helpers import predict_contract_address
from database import SupabaseDB
from transaction_monitor import TransactionMonitor, TransactionState
import logging
import asyncio
from datetime import datetime, timedelta
from config import config

# Conversation states
WAITING_FOR_ADDRESS, WAITING_FOR_SENDER, WAITING_FOR_SUBSCRIPTION_ADDRESS = range(3)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def is_subscribed(subscription: dict) -> bool:
    logger.debug(f"[DEBUG] Checking subscription: {subscription}")
    if not subscription or not subscription.get("is_active"):
        logger.debug("[DEBUG] Subscription not active or not found")
        return False
    expiry_date = subscription.get("expiry_date")
    if expiry_date:
        is_valid = datetime.fromisoformat(expiry_date) > datetime.now()
        logger.debug(f"[DEBUG] Expiry date: {expiry_date}, Valid: {is_valid}")
        return is_valid
    logger.debug("[DEBUG] No expiry date, assuming invalid")
    return False

def get_network_config(network: str) -> str:
    if network == "mainnet":
        return config["mainnet_rpc_url"]
    return config["sepolia_rpc_url"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    supabase: SupabaseDB = context.bot_data["supabase"]
    user = update.effective_user
    supabase.add_user(telegram_id=user.id, username=user.username or "unknown")
    subscription = supabase.get_subscription(telegram_id=user.id)
    network = get_network_config("mainnet")
    network_indicator = "🟢 Mainnet"
    if is_subscribed(subscription):
        keyboard = [
            [InlineKeyboardButton("🔮 Predict Contract", callback_data="predict")],
            [InlineKeyboardButton("💸 Monitor Payment", callback_data="monitor")],
            [
                InlineKeyboardButton("💰 Check Balance", callback_data="balance"),
                InlineKeyboardButton("ℹ️ Token Info", callback_data="tokeninfo"),
            ],
            [
                InlineKeyboardButton("📋 View Watchlist", callback_data="watchlist"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
            ],
            [InlineKeyboardButton(f"{network_indicator}", callback_data="toggle_network")],

            [InlineKeyboardButton("❓ Help", callback_data="help")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"👋 *Welcome back, {user.first_name or user.username}!*\n\n"
            "Select an option to get started:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        logger.info(f"User {user.id} (subscribed) started the bot.")
    else:
        await update.message.reply_text(
            "👋 *Welcome to Contract Predictor Bot!*\n\n"
            "Unlock powerful tools for Ethereum contract management:\n"
            "• *🔮 Predict Contract*: Generate future contract addresses based on sender and nonce.\n"
            "• *💸 Monitor Payment*: Track Ethereum transactions in real-time.\n"
            "• *📋 View Watchlist*: Save and manage predicted addresses.\n"
            "• *💰 Check Balance*: Check wallet balances (coming soon).\n"
            "• *ℹ️ Token Info*: Get token details (coming soon).\n"
            "• *⚙️ Settings*: Customize your experience (coming soon).\n\n"
            "💎 *Subscribe now for just 0.01 ETH/month* to access all features!\n"
            "Use the button below to get started or type /help for more info.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 Subscribe Now", callback_data="subscribe")]]),
            parse_mode="Markdown"
        )
        logger.info(f"User {user.id} (not subscribed) started the bot.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    supabase: SupabaseDB = context.bot_data["supabase"]
    user_id = query.from_user.id
    network = "mainnet" if config.get("rpc_url") == config.get("mainnet_rpc_url") else "sepolia"
    network_indicator = "🟢 Mainnet" if network == "mainnet" else "🔴 Sepolia"
    data = query.data
    logger.info(f"Button callback received: user_id={user_id}, callback_data={data}")

    subscription = supabase.get_subscription(telegram_id=user_id)

    if data == "main_menu":
        if is_subscribed(subscription):
            keyboard = [
                [InlineKeyboardButton("🔮 Predict Contract", callback_data="predict")],
                [InlineKeyboardButton("💸 Monitor Payment", callback_data="monitor")],
                [
                    InlineKeyboardButton("💰 Check Balance", callback_data="balance"),
                    InlineKeyboardButton("ℹ️ Token Info", callback_data="tokeninfo"),
                ],
                [
                    InlineKeyboardButton("📋 View Watchlist", callback_data="watchlist"),
                    InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
                ],
                [InlineKeyboardButton(f"{network_indicator}", callback_data="toggle_network")],
                [InlineKeyboardButton("❓ Help", callback_data="help")],
            ]
            await query.edit_message_text(
                f"👋 *Welcome back, {query.from_user.first_name or query.from_user.username}!*\n\n"
                "Select an option to get started:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "👋 *Welcome to Contract Predictor Bot!*\n\n"
                "Unlock powerful tools for Ethereum contract management:\n"
                "• *🔮 Predict Contract*: Generate future contract addresses based on sender and nonce.\n"
                "• *💸 Monitor Payment*: Track Ethereum transactions in real-time.\n"
                "• *📋 View Watchlist*: Save and manage predicted addresses.\n"
                "• *💰 Check Balance*: Check wallet balances (coming soon).\n"
                "• *ℹ️ Token Info*: Get token details (coming soon).\n"
                "• *⚙️ Settings*: Customize your experience (coming soon).\n\n"
                "💎 *Subscribe now for just 0.01 ETH/month* to access all features!\n"
                "Use the button below to get started or type /help for more info.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 Subscribe Now", callback_data="subscribe")]]),
                parse_mode="Markdown"
            )
        logger.info(f"User {user_id} returned to main menu (subscribed={is_subscribed(subscription)})")
        return ConversationHandler.END
    elif data == "toggle_network":
        if network == "mainnet":
            config["rpc_url"] = config["sepolia_rpc_url"]
            network = "sepolia"
            network_indicator = "🔴 Sepolia"
        else:
            config["rpc_url"] = config["mainnet_rpc_url"]
            network = "mainnet"
            network_indicator = "🟢 Mainnet"
        logger.info(f"New RPC URL: {config['rpc_url']}")
        if is_subscribed(subscription):
            keyboard = [
                [InlineKeyboardButton("🔮 Predict Contract", callback_data="predict")],
                [InlineKeyboardButton("💸 Monitor Payment", callback_data="monitor")],
                [
                    InlineKeyboardButton("💰 Check Balance", callback_data="balance"),
                    InlineKeyboardButton("ℹ️ Token Info", callback_data="tokeninfo"),
                ],
                [
                    InlineKeyboardButton("📋 View Watchlist", callback_data="watchlist"),
                    InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
                ],
                [InlineKeyboardButton(f"{network_indicator}", callback_data="toggle_network")],
                [InlineKeyboardButton("❓ Help", callback_data="help")],
            ]
            await query.edit_message_text(
                f"👋 *Welcome back, {query.from_user.first_name or query.from_user.username}!*\n\n"
                "Select an option to get started:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "👋 *Welcome to Contract Predictor Bot!*\n\n"
                "Unlock powerful tools for Ethereum contract management:\n"
                "• *🔮 Predict Contract*: Generate future contract addresses based on sender and nonce.\n"
                "• *💸 Monitor Payment*: Track Ethereum transactions in real-time.\n"
                "• *📋 View Watchlist*: Save and manage predicted addresses.\n"
                "• *💰 Check Balance*: Check wallet balances (coming soon).\n"
                "• *ℹ️ Token Info*: Get token details (coming soon).\n"
                "• *⚙️ Settings*: Customize your experience (coming soon).\n\n"
                "💎 *Subscribe now for just 0.01 ETH/month* to access all features!\n"
                "Use the button below to get started or type /help for more info.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 Subscribe Now", callback_data="subscribe")]]),
                parse_mode="Markdown"
            )
        logger.info(f"User {user_id} toggled network to {network}")
        return ConversationHandler.END
    print("Subscription status:", is_subscribed(subscription), "Callback data:", data)
    if not is_subscribed(subscription) and data not in ["subscribe", "help"] and not data.startswith("confirm_subscribe_"):
        logger.debug(f"[DEBUG] Subscription check failed for user {user_id}, data: {data}, subscription: {subscription}")
        await query.edit_message_text(
            "🔒 *Subscription Required*\n\n"
            "Please subscribe to access this feature. It’s just 0.01 ETH/month!\n"
            "Use the button below to subscribe or type /help for more info.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Subscribe Now", callback_data="subscribe")],
                [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
            ]),
            parse_mode="Markdown"
        )
        logger.info(f"User {user_id} attempted restricted feature: {data}")
        logger.debug(f"[DEBUG] Returning ConversationHandler.END due to subscription restriction")
        return ConversationHandler.END

    if data == "subscribe":
        logger.debug(f"[DEBUG] Entering subscribe flow for user {user_id}")
        try:
            logger.debug(f"[DEBUG] Checking config for recipient_address: {config.get('recipient_address')}")
            if not config.get('recipient_address'):
                raise ValueError("Recipient address not configured in config.py")
            logger.debug(f"[DEBUG] Attempting to edit message for user {user_id}")
            await query.edit_message_text(
                "💎 *Subscribe to Contract Predictor Bot*\n\n"
                f"Please send the sender address (0x...) to initiate a payment of 0.01 ETH to `{config['recipient_address']}`.\n"
                "⚠️ *Do not close this window* until payment confirmation is received.\n"
                f"Monitoring will timeout after {config['max_blocks_to_wait']} blocks (~{config['max_blocks_to_wait'] * 12 // 60} minutes).",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Cancel", callback_data="main_menu")]])
            )
            logger.debug(f"[DEBUG] Message edited successfully for user {user_id}")
            logger.debug(f"[DEBUG] Returning WAITING_FOR_SUBSCRIPTION_ADDRESS for user {user_id}")
            return WAITING_FOR_SUBSCRIPTION_ADDRESS
        except Exception as e:
            logger.error(f"[ERROR] Exception in subscribe flow for user {user_id}: {e}")
            await query.edit_message_text(
                f"❌ *Error*: An unexpected error occurred. Please try again or contact support at ajstylesmb@gmail.com.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Try Again", callback_data="subscribe")],
                    [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
                ])
            )
            logger.debug(f"[DEBUG] Returned to ConversationHandler.END due to error for user {user_id}")
            return ConversationHandler.END
    
    elif data == "predict":
        await query.edit_message_text(
            "🔮 *Predict Contract Address*\n\n"
            "Please send the sender address (0x...):",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]])
        )
        logger.info(f"User {user_id} entered predict flow")
        return WAITING_FOR_ADDRESS

    elif data == "monitor":
        await query.edit_message_text(
            "💸 *Monitor Payment*\n\n"
            "Please send the sender address (0x...) to monitor for payments:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]])
        )
        logger.info(f"User {user_id} entered monitor flow")
        return WAITING_FOR_SENDER

    elif data == "watchlist":
        watchlist = supabase.get_watchlist(telegram_id=user_id)
        if not watchlist:
            await query.edit_message_text(
                "📋 *Your Watchlist*\n\n"
                "No addresses in your watchlist yet.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]])
            )
            logger.info(f"User {user_id} viewed empty watchlist")
            return ConversationHandler.END

        response = "📋 *Your Watchlist*\n\n"
        keyboard = []
        for entry in watchlist:
            response += (
                f"🔹 *Entry {entry['id']}*\n"
                f"  • Sender: `{entry['sender_address']}`\n"
                f"  • Nonce: `{entry['nonce']}`\n"
                f"  • Predicted: `{entry['predicted_address']}`\n"
                f"  • Added: `{entry['created_at']}`\n\n"
            )
            keyboard.append([InlineKeyboardButton(f"🗑️ Delete Entry {entry['id']}", callback_data=f"delete_{entry['id']}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(response, reply_markup=reply_markup, parse_mode="Markdown")
        logger.info(f"User {user_id} viewed watchlist")
        return ConversationHandler.END

    elif data.startswith("delete_"):
        entry_id = int(data.split("_")[1])
        success = supabase.delete_watchlist_entry(entry_id=entry_id, telegram_id=user_id)
        text = "✅ *Entry deleted successfully!*" if success else "❌ *Failed to delete entry.*"
        await query.edit_message_text(
            f"{text}\n\nSelect an option to continue:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 View Watchlist", callback_data="watchlist")],
                [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
            ])
        )
        logger.info(f"User {user_id} deleted watchlist entry {entry_id}")
        return ConversationHandler.END

    elif data == "help":
        await query.edit_message_text(
            "❓ *Help Menu*\n\n"
            "• *🔮 Predict Contract*: Generate a predicted contract address.\n"
            "• *💸 Monitor Payment*: Monitor Ethereum transactions from a sender.\n"
            "• *📋 View Watchlist*: See your saved predictions.\n"
            "• *💰 Check Balance*: Coming soon!\n"
            "• *ℹ️ Token Info*: Coming soon!\n"
            "• *⚙️ Settings*: Coming soon!\n"
            "• *📝 Check Subscription*: Use /subscription to view your subscription status.\n"
            "\nUse /start to return to the main menu.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]])
        )
        logger.info(f"User {user_id} viewed help menu")
        return ConversationHandler.END

    elif data.startswith("confirm_predict_"):
        sender = data.split("confirm_predict_")[1]
        try:
            web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/111dffff7e304bb6ac87dfa3eedda096'))
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
            keyboard = [
                [InlineKeyboardButton("📋 View Watchlist", callback_data="watchlist")],
                [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
            ]
            await query.edit_message_text(
                message,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            logger.info(f"User {user_id} completed prediction for sender {sender}")
        except Exception as e:
            logger.error(f"Error in predict confirmation for user {user_id}: {e}")
            await query.edit_message_text(
                f"❌ *Error*: {e}\n\nTry again or return to the main menu.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]])
            )
        return ConversationHandler.END

    elif data.startswith("confirm_monitor_"):
        sender = data.split("confirm_monitor_")[1]
        try:
            monitor = TransactionMonitor(config["rpc_url"])
            context.bot_data["monitor"] = monitor
            await query.edit_message_text(
                f"🔍 *Monitoring Payment*\n\n"
                f"Monitoring transactions from `{sender}` to `{config['recipient_address']}`.\n"
                f"Expected amount: `{config['expected_amount']} ETH`.\n"
                f"Will monitor for {config['max_blocks_to_wait']} blocks (~{config['max_blocks_to_wait'] * 12 // 60} minutes).\n\n"
                f"⚠️ *Do not close this window* until confirmation is received.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Cancel Monitoring", callback_data="main_menu")]])
            )
            logger.info(f"User {user_id} started monitoring for sender {sender}")

            result = await monitor.monitor_transaction(sender)
            await monitor.destroy()
            del context.bot_data["monitor"]

            if result == TransactionState.FOUND_CORRECT_AMOUNT:
                message = (
                    f"✅ *Payment Confirmed!*\n\n"
                    f"Expected amount of `{config['expected_amount']} ETH` or more received."
                )
            elif result == TransactionState.FOUND_INCORRECT_AMOUNT:
                message = (
                    f"⚠️ *Incorrect Payment Amount!*\n\n"
                    f"Found transactions, but none met the expected amount of `{config['expected_amount']} ETH`.\n"
                    f"Details:\n"
                )
                for tx in monitor.found_transactions:
                    message += f"• Hash: `{tx['hash']}`\n  Amount: `{tx['amount']} ETH`\n"
            elif result == TransactionState.TIMEOUT:
                message = (
                    f"⏰ *Monitoring Timeout!*\n\n"
                    f"No matching transactions found within {config['max_blocks_to_wait']} blocks.\n"
                    "If you have paid, please contact support at ajstylesmb@gmail.com."
                )
            else:
                message = "❓ *Unexpected Result*\n\nPlease try again or contact support at ajstylesmb@gmail.com."

            await query.message.reply_text(
                message,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Try Again", callback_data="monitor")],
                    [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
                ])
            )
            logger.info(f"User {user_id} completed monitoring with result: {result}")
        except Exception as e:
            logger.error(f"Error in monitor confirmation for user {user_id}: {e}")
            await query.edit_message_text(
                f"❌ *Error*: {e}\n\nTry again or return to the main menu.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]])
            )
            if "monitor" in context.bot_data:
                await context.bot_data["monitor"].destroy()
                del context.bot_data["monitor"]
        return ConversationHandler.END 

    elif data.startswith("confirm_subscribe_"):
        logger.debug(f"[DEBUG] Entering confirm_subscribe flow for callback data: {data}")
        sender = data.split("confirm_subscribe_")[1]
        logger.debug(f"[DEBUG] Extracted sender address: {sender}")
        try:
            logger.debug("[DEBUG] Initializing TransactionMonitor")
            monitor = TransactionMonitor(config["rpc_url"])
            context.bot_data["monitor"] = monitor
            logger.debug(f"[DEBUG] Monitor initialized, starting message update for sender: {sender}")
            await query.edit_message_text(
                f"🔍 *Monitoring Subscription Payment*\n\n"
                f"Monitoring transactions from `{sender}` to `{config['recipient_address']}`.\n"
                "Expected amount: `0.01 ETH`.\n"
                f"Will monitor for {config['max_blocks_to_wait']} blocks (~{config['max_blocks_to_wait'] * 12 // 60} minutes).\n\n"
                f"⚠️ *Do not close this window* until confirmation is received.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Cancel Monitoring", callback_data="main_menu")]])
            )
            logger.debug("[DEBUG] Message updated, starting monitor_transaction")
            # Override config for subscription payment
            original_amount = config["expected_amount"]
            config["expected_amount"] = 0.01
            result = await monitor.monitor_transaction(sender)
            config["expected_amount"] = original_amount  # Restore original amount
            logger.debug(f"[DEBUG] Monitor_transaction returned: {result}")
            await monitor.destroy()
            del context.bot_data["monitor"]

            # Check current subscription before update
            current_subscription = supabase.get_subscription(telegram_id=user_id)
            logger.debug(f"[DEBUG] Subscription before update: {current_subscription}")

            if result == TransactionState.FOUND_CORRECT_AMOUNT:
                expiry_date = (datetime.now() + timedelta(days=30)).isoformat()
                subscription = supabase.get_subscription(telegram_id=user_id)
                logger.debug(f"[DEBUG] Current subscription data: {subscription}")
                if subscription:
                    logger.debug("[DEBUG] Updating existing subscription")
                    supabase.update_subscription(telegram_id=user_id, is_active=True, expiry_date=expiry_date)
                else:
                    logger.debug("[DEBUG] Creating new subscription")
                    supabase.add_subscription(telegram_id=user_id, recipient_address=config["recipient_address"])
                    supabase.update_subscription(telegram_id=user_id, is_active=True, expiry_date=expiry_date)
                # Verify update
                updated_subscription = supabase.get_subscription(telegram_id=user_id)
                logger.debug(f"[DEBUG] Subscription after update: {updated_subscription}")
                message = (
                    f"✅ *Subscription Activated!*\n\n"
                    "You now have full access to all features for 30 days!\n"
                    f"Expiry: `{expiry_date}`\n\n"
                    "Use /start to access the main menu."
                )
                keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]]
            elif result == TransactionState.FOUND_INCORRECT_AMOUNT:
                message = (
                    f"⚠️ *Incorrect Payment Amount!*\n\n"
                    f"Found transactions, but none met the expected amount of `0.01 ETH`.\n"
                    f"Details:\n"
                )
                for tx in monitor.found_transactions:
                    message += f"• Hash: `{tx['hash']}`\n  Amount: `{tx['amount']} ETH`\n"
                message += "\nIf you have paid, please contact support at ajstylesmb@gmail.com."
                keyboard = [
                    [InlineKeyboardButton("🔄 Try Again", callback_data="subscribe")],
                    [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
                ]
                logger.debug("[DEBUG] Incorrect payment amount detected")
            elif result == TransactionState.TIMEOUT:
                message = (
                    f"⏰ *Monitoring Timeout!*\n\n"
                    f"No matching transactions found within {config['max_blocks_to_wait']} blocks.\n"
                    "If you have paid, please contact support at ajstylesmb@gmail.com."
                )
                keyboard = [
                    [InlineKeyboardButton("🔄 Try Again", callback_data="subscribe")],
                    [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
                ]
                logger.debug("[DEBUG] Monitoring timed out")
            else:
                message = "❓ *Unexpected Result*\n\nPlease try again or contact support at ajstylesmb@gmail.com."
                keyboard = [
                    [InlineKeyboardButton("🔄 Try Again", callback_data="subscribe")],
                    [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
                ]
                logger.debug("[DEBUG] Unexpected monitor result")

            await query.message.reply_text(
                message,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            logger.debug("[DEBUG] Response message sent")
        except Exception as e:
            logger.error(f"[ERROR] Exception in confirm_subscribe for user {user_id}: {e}")
            await query.edit_message_text(
                f"❌ *Error*: {e}\n\nTry again or contact support at ajstylesmb@gmail.com.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Try Again", callback_data="subscribe")],
                    [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
                ])
            )
            if "monitor" in context.bot_data:
                await context.bot_data["monitor"].destroy()
                del context.bot_data["monitor"]
            logger.debug("[DEBUG] Returned to ConversationHandler.END due to error")
        return ConversationHandler.END

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    supabase: SupabaseDB = context.bot_data["supabase"]
    sender = update.message.text.strip()
    try:
        if not Web3.is_address(sender):
            await update.message.reply_text(
                "❌ *Invalid Address*\n\n"
                "Please send a valid Ethereum address (0x...) or cancel.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Try Again", callback_data="predict")],
                    [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
                ])
            )
            logger.info(f"User {update.effective_user.id} entered invalid address for predict: {sender}")
            return WAITING_FOR_ADDRESS

        await update.message.reply_text(
            f"🔮 *Confirm Sender Address*\n\n"
            f"You entered: `{sender}`\n"
            "Is this correct?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_predict_{sender}")],
                [InlineKeyboardButton("🔄 Change Address", callback_data="predict")],
                [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
            ])
        )
        context.user_data["pending_sender"] = sender
        logger.info(f"User {update.effective_user.id} confirmed address for predict: {sender}")
        return WAITING_FOR_ADDRESS
    except Exception as e:
        logger.error(f"Error in get_address for user {update.effective_user.id}: {e}")
        await update.message.reply_text(
            f"❌ *Error*: {e}\n\nTry again or return to the main menu.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]])
        )
        return ConversationHandler.END

async def get_sender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sender = update.message.text.strip()
    try:
        if not Web3.is_address(sender):
            await update.message.reply_text(
                "❌ *Invalid Address*\n\n"
                "Please send a valid Ethereum address (0x...) or cancel.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Try Again", callback_data="monitor")],
                    [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
                ])
            )
            logger.info(f"User {update.effective_user.id} entered invalid address for monitor: {sender}")
            return WAITING_FOR_SENDER

        await update.message.reply_text(
            f"💸 *Confirm Sender Address*\n\n"
            f"You entered: `{sender}`\n"
            "Is this correct?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_monitor_{sender}")],
                [InlineKeyboardButton("🔄 Change Address", callback_data="monitor")],
                [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
            ])
        )
        context.user_data["pending_sender"] = sender
        logger.info(f"User {update.effective_user.id} confirmed address for monitor: {sender}")
        return WAITING_FOR_SENDER
    except Exception as e:
        logger.error(f"Error in get_sender for user {update.effective_user.id}: {e}")
        await update.message.reply_text(
            f"❌ *Error*: {e}\n\nTry again or return to the main menu.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]])
        )
        return ConversationHandler.END

async def get_subscription_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    supabase: SupabaseDB = context.bot_data["supabase"]
    sender = update.message.text.strip()
    logger.debug(f"[DEBUG] Received sender address '{sender}' for subscription from user {update.effective_user.id}")
    try:
        if not Web3.is_address(sender):
            logger.debug(f"[DEBUG] Invalid address '{sender}' detected for user {update.effective_user.id}")
            await update.message.reply_text(
                "❌ *Invalid Address*\n\n"
                "Please send a valid Ethereum address (0x...) or cancel.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Try Again", callback_data="subscribe")],
                    [InlineKeyboardButton("⬅️ Cancel", callback_data="main_menu")]
                ])
            )
            return WAITING_FOR_SUBSCRIPTION_ADDRESS

        logger.debug(f"[DEBUG] Valid address '{sender}' confirmed for user {update.effective_user.id}")
        await update.message.reply_text(
            f"💎 *Confirm Subscription Payment*\n\n"
            f"Sender: `{sender}`\n"
            f"Recipient: `{config['recipient_address']}`\n"
            "Amount: `0.01 ETH`\n"
            f"Timeout: ~{config['max_blocks_to_wait'] * 12 // 60} minutes\n\n"
            "Is this correct? Confirm to start monitoring.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_subscribe_{sender}")],
                [InlineKeyboardButton("🔄 Change Address", callback_data="subscribe")],
                [InlineKeyboardButton("⬅️ Cancel", callback_data="main_menu")]
            ])
        )
        context.user_data["pending_sender"] = sender
        logger.debug(f"[DEBUG] Confirmation prompt sent for user {update.effective_user.id} with sender {sender}")
        return WAITING_FOR_SUBSCRIPTION_ADDRESS
    except Exception as e:
        logger.error(f"[ERROR] Exception in get_subscription_address for user {update.effective_user.id}: {e}")
        await update.message.reply_text(
            f"❌ *Error*: {e}\n\nTry again or return to the main menu.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]])
        )
        return ConversationHandler.END
async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    supabase: SupabaseDB = context.bot_data["supabase"]
    user_id = update.effective_user.id
    subscription = supabase.get_subscription(telegram_id=user_id)

    if not is_subscribed(subscription):
        await update.message.reply_text(
            "🔒 *Subscription Required*\n\n"
            "Please subscribe to access your watchlist. It’s just 0.01 ETH/month!\n"
            "Use the button below to subscribe or type /help for more info.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Subscribe Now", callback_data="subscribe")],
                [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
            ])
        )
        logger.info(f"User {user_id} attempted watchlist without subscription")
        return

    watchlist = supabase.get_watchlist(telegram_id=user_id)
    if not watchlist:
        await update.message.reply_text(
            "📋 *Your Watchlist*\n\n"
            "No addresses in your watchlist yet.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]])
        )
        logger.info(f"User {user_id} viewed empty watchlist")
        return

    response = "📋 *Your Watchlist*\n\n"
    keyboard = []
    for entry in watchlist:
        response += (
            f"🔹 *Entry {entry['id']}*\n"
            f"  • Sender: `{entry['sender_address']}`\n"
            f"  • Nonce: `{entry['nonce']}`\n"
            f"  • Predicted: `{entry['predicted_address']}`\n"
            f"  • Added: `{entry['created_at']}`\n\n"
        )
        keyboard.append([InlineKeyboardButton(f"🗑️ Delete Entry {entry['id']}", callback_data=f"delete_{entry['id']}")])
    keyboard.append([InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")
    logger.info(f"User {user_id} viewed watchlist")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "❓ *Help Menu*\n\n"
        "• *🔮 Predict Contract*: Generate a predicted contract address.\n"
        "• *💸 Monitor Payment*: Monitor Ethereum transactions from a sender.\n"
        "• *📋 View Watchlist*: See your saved predictions.\n"
        "• *💰 Check Balance*: Coming soon!\n"
        "• *ℹ️ Token Info*: Coming soon!\n"
        "• *⚙️ Settings*: Coming soon!\n"
        "• *📝 Check Subscription*: Use /subscription to view your subscription status.\n"
        "\nUse /start to return to the main menu.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]])
    )
    logger.info(f"User {update.effective_user.id} viewed help menu")

async def subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    supabase: SupabaseDB = context.bot_data["supabase"]
    subscription = supabase.get_subscription(telegram_id=update.effective_user.id)
    if is_subscribed(subscription):
        expiry_date = subscription.get("expiry_date", "N/A")
        await update.message.reply_text(
            f"📝 *Subscription Status*\n\n"
            f"Status: *Active*\n"
            f"Expiry Date: `{expiry_date}`\n\n"
            "Use /start to access the main menu.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]])
        )
        logger.info(f"User {update.effective_user.id} checked subscription: active, expires {expiry_date}")
    else:
        await update.message.reply_text(
            "📝 *Subscription Status*\n\n"
            "Status: *Not Subscribed*\n\n"
            "Subscribe for just 0.01 ETH/month to unlock all features!\n"
            "Use the button below to subscribe or type /help for more info.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Subscribe Now", callback_data="subscribe")],
                [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
            ])
        )
        logger.info(f"User {update.effective_user.id} checked subscription: not subscribed")