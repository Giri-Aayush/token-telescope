from supabase import create_client
from datetime import datetime
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class SupabaseDB:
    def __init__(self, url: str, key: str):
        self.client = create_client(url, key)

    def add_user(self, telegram_id: int, username: str) -> bool:
        try:
            existing_user = (self.client.table("users")
                           .select("*")
                           .eq("telegram_id", telegram_id)
                           .execute().data)

            if not existing_user:
                data = {"telegram_id": telegram_id, "username": username}
                self.client.table("users").insert(data).execute()
                logger.info(f"Added new user: {telegram_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding user {telegram_id}: {e}")
            return False

    def get_watchlist(self, telegram_id: int) -> List[Dict]:
        try:
            response = (self.client.table("watchlist")
                       .select("*")
                       .eq("telegram_id", telegram_id)
                       .execute())
            return response.data
        except Exception as e:
            logger.error(f"Error fetching watchlist for user {telegram_id}: {e}")
            return []

    def add_watchlist_entry(self, telegram_id: int, sender_address: str, 
                          nonce: int, predicted_address: str) -> bool:
        try:
            existing_entry = (self.client.table("watchlist")
                            .select("*")
                            .eq("telegram_id", telegram_id)
                            .eq("predicted_address", predicted_address)
                            .execute().data)
            
            if existing_entry:
                logger.info(f"Watchlist entry already exists for user {telegram_id}")
                return False

            data = {
                "telegram_id": telegram_id,
                "sender_address": sender_address,
                "nonce": nonce,
                "predicted_address": predicted_address,
                "created_at": datetime.now().isoformat()
            }
            
            self.client.table("watchlist").insert(data).execute()
            logger.info(f"Added watchlist entry for user {telegram_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding watchlist entry for user {telegram_id}: {e}")
            return False

    def delete_watchlist_entry(self, entry_id: int, telegram_id: int) -> bool:
        try:
            (self.client.table("watchlist")
             .delete()
             .eq("id", entry_id)
             .eq("telegram_id", telegram_id)
             .execute())
            logger.info(f"Deleted watchlist entry {entry_id} for user {telegram_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting watchlist entry {entry_id}: {e}")
            return False

    def add_subscription(self, telegram_id: int, recipient_address: str) -> bool:
        try:
            existing_sub = (self.client.table("subscriptions")
                          .select("*")
                          .eq("telegram_id", telegram_id)
                          .execute().data)
            
            if existing_sub:
                logger.info(f"Subscription already exists for user {telegram_id}")
                return False

            self.client.table("subscriptions").insert({
                "telegram_id": telegram_id,
                "recipient_address": recipient_address,
                "is_active": False
            }).execute()
            
            logger.info(f"Added subscription for user {telegram_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding subscription for user {telegram_id}: {e}")
            return False

    def update_subscription(self, telegram_id: int, is_active: bool, 
                          expiry_date: str = None) -> bool:
        try:
            data = {"is_active": is_active}
            if expiry_date:
                data["expiry_date"] = expiry_date
                
            (self.client.table("subscriptions")
             .update(data)
             .eq("telegram_id", telegram_id)
             .execute())
             
            logger.info(f"Updated subscription for user {telegram_id}: "
                       f"active={is_active}, expires={expiry_date}")
            return True
        except Exception as e:
            logger.error(f"Error updating subscription for user {telegram_id}: {e}")
            return False

    def get_subscription(self, telegram_id: int) -> Optional[Dict]:
        try:
            response = (self.client.table("subscriptions")
                       .select("*")
                       .eq("telegram_id", telegram_id)
                       .execute())
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching subscription for user {telegram_id}: {e}")
            return None