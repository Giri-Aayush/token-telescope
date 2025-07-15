from supabase import create_client
from datetime import datetime
import logging
# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class SupabaseDB:
    def __init__(self, url: str, key: str):
        self.client = create_client(url, key)

    # Existing methods (e.g., add_user, get_watchlist, delete_watchlist_entry)
    def add_user(self, telegram_id: int, username: str):
        data = {"telegram_id": telegram_id, "username": username}
        # Check if user already exists
        existing_user = self.client.table("users").select("*").eq("telegram_id", telegram_id).execute().data

        if not existing_user:
            self.client.table("users").insert(data).execute()

    def get_watchlist(self, telegram_id: int):

        return self.client.table("watchlist").select("*").eq("telegram_id", telegram_id).execute().data

    def add_watchlist_entry(self, telegram_id: int, sender_address: str, nonce: int, predicted_address: str):
        data = {
            "telegram_id": telegram_id,
            "sender_address": sender_address,
            "nonce": nonce,
            "predicted_address": predicted_address,
            "created_at": datetime.now().isoformat()
        }
        try:
            self.client.table("watchlist").insert(data).execute()
            logger.info(f"Added watchlist entry for user {telegram_id}: {data}")
            return True
        except Exception as e:
            logger.error(f"Error adding watchlist entry for user {telegram_id}: {e}")
            return False

    def delete_watchlist_entry(self, entry_id: int, telegram_id: int):
        try:
            self.client.table("watchlist").delete().eq("id", entry_id).eq("telegram_id", telegram_id).execute()
            logger.info(f"Deleted watchlist entry {entry_id} for user {telegram_id}")
            return True
        except:
            return False
        
    # New methods for subscriptions
    def add_subscription(self, telegram_id: int, recipient_address: str) -> bool:
        try:
            self.client.table("subscriptions").insert({
                "telegram_id": telegram_id,
                "recipient_address": recipient_address,
                "is_active": False
            }).execute()
            logger.info(f"Subscription added for user {telegram_id} with address {recipient_address}")
            return True
        except Exception as e:
            logger.error(f"Error adding subscription: {e}")
            return False

    def update_subscription(self, telegram_id: int, is_active: bool, expiry_date: str = None) -> bool:
        try:
            data = {"is_active": is_active}
            if expiry_date:
                data["expiry_date"] = expiry_date
            self.client.table("subscriptions").update(data).eq("telegram_id", telegram_id).execute()
            logger.info(f"Subscription updated for user {telegram_id}: is_active={is_active}, expiry_date={expiry_date}")
            return True
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            return False

    def get_subscription(self, telegram_id: int) -> dict:
        try:
            response = self.client.table("subscriptions").select("*").eq("telegram_id", telegram_id).execute()
            logger.info(f"Fetched subscription for user {telegram_id}: {response.data}")
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error fetching subscription: {e}")
            return {}