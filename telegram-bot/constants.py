from enum import Enum

WAITING_FOR_ADDRESS, WAITING_FOR_SENDER, WAITING_FOR_SUBSCRIPTION_ADDRESS = range(3)

class TransactionState(Enum):
    WAITING = "WAITING"
    FOUND_INCORRECT_AMOUNT = "FOUND_INCORRECT_AMOUNT"
    FOUND_CORRECT_AMOUNT = "FOUND_CORRECT_AMOUNT"
    TIMEOUT = "TIMEOUT"

class Messages:
    SUBSCRIPTION_REQUIRED = (
        "🔒 *Subscription Required*\n\n"
        "Please subscribe to access this feature. It's just 0.01 ETH/month!\n"
        "Use the button below to subscribe or type /help for more info."
    )
    
    WELCOME_SUBSCRIBED = (
        "👋 *Welcome back, {}!*\n\n"
        "Select an option to get started:"
    )
    
    WELCOME_UNSUBSCRIBED = (
        "👋 *Welcome to Contract Predictor Bot!*\n\n"
        "Unlock powerful tools for Ethereum contract management:\n"
        "• *🔮 Predict Contract*: Generate future contract addresses based on sender and nonce.\n"
        "• *💸 Monitor Payment*: Track Ethereum transactions in real-time.\n"
        "• *📋 View Watchlist*: Save and manage predicted addresses.\n"
        "• *💰 Check Balance*: Check wallet balances (coming soon).\n"
        "• *ℹ️ Token Info*: Get token details (coming soon).\n"
        "• *⚙️ Settings*: Customize your experience (coming soon).\n\n"
        "💎 *Subscribe now for just 0.01 ETH/month* to access all features!\n"
        "Use the button below to get started or type /help for more info."
    )
    
    INVALID_ADDRESS = (
        "❌ *Invalid Address*\n\n"
        "Please send a valid Ethereum address (0x...) or cancel."
    )
    
    HELP_TEXT = (
        "❓ *Help Menu*\n\n"
        "• *🔮 Predict Contract*: Generate a predicted contract address.\n"
        "• *💸 Monitor Payment*: Monitor Ethereum transactions from a sender.\n"
        "• *📋 View Watchlist*: See your saved predictions.\n"
        "• *💰 Check Balance*: Coming soon!\n"
        "• *ℹ️ Token Info*: Coming soon!\n"
        "• *⚙️ Settings*: Coming soon!\n"
        "• *📝 Check Subscription*: Use /subscription to view your subscription status.\n"
        "\nUse /start to return to the main menu."
    )