from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List

class KeyboardFactory:
    @staticmethod
    def main_menu_subscribed(network_indicator: str) -> InlineKeyboardMarkup:
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
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def main_menu_unsubscribed(network_indicator: str) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("💎 Subscribe Now", callback_data="subscribe")],
            [InlineKeyboardButton(f"{network_indicator}", callback_data="toggle_network")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def subscription_required() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Subscribe Now", callback_data="subscribe")],
            [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
        ])
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
        ])
    
    @staticmethod
    def cancel_action() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Cancel", callback_data="main_menu")]
        ])
    
    @staticmethod
    def confirm_action(action: str, data: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}_{data}")],
            [InlineKeyboardButton("🔄 Change Address", callback_data=action)],
            [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
        ])
    
    @staticmethod
    def watchlist_actions(entries: List[dict]) -> InlineKeyboardMarkup:
        keyboard = []
        for entry in entries:
            keyboard.append([
                InlineKeyboardButton(
                    f"🗑️ Delete Entry {entry['id']}", 
                    callback_data=f"delete_{entry['id']}"
                )
            ])
        keyboard.append([InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def retry_or_back(action: str = None) -> InlineKeyboardMarkup:
        keyboard = []
        if action:
            keyboard.append([InlineKeyboardButton("🔄 Try Again", callback_data=action)])
        keyboard.append([InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")])
        return InlineKeyboardMarkup(keyboard)