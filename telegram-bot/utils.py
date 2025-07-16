from web3 import Web3
import rlp
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def predict_contract_address(sender: str, nonce: int) -> str:
    encoded = Web3.keccak(rlp.encode([Web3.to_bytes(hexstr=sender), nonce]))[12:]
    return Web3.to_checksum_address(encoded)

def is_subscribed(subscription: dict) -> bool:
    logger.debug(f"Checking subscription: {subscription}")
    
    if not subscription or not subscription.get("is_active"):
        logger.debug("Subscription not active or not found")
        return False
    
    expiry_date = subscription.get("expiry_date")
    if expiry_date:
        is_valid = datetime.fromisoformat(expiry_date) > datetime.now()
        logger.debug(f"Expiry date: {expiry_date}, Valid: {is_valid}")
        return is_valid
    
    logger.debug("No expiry date, assuming invalid")
    return False

def validate_eth_address(address: str) -> bool:
    return Web3.is_address(address)

def format_watchlist_entry(entry: dict) -> str:
    return (
        f"🔹 *Entry {entry['id']}*\n"
        f"  • Sender: `{entry['sender_address']}`\n"
        f"  • Nonce: `{entry['nonce']}`\n"
        f"  • Predicted: `{entry['predicted_address']}`\n"
        f"  • Added: `{entry['created_at']}`\n\n"
    )