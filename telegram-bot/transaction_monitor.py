# transaction_monitor.py
import asyncio
from enum import Enum
from web3 import Web3
from web3.types import BlockData, TxData
from typing import List, Dict, Optional
from config import config
import logging

logger = logging.getLogger(__name__)

class TransactionState(Enum):
    WAITING = "WAITING"
    FOUND_INCORRECT_AMOUNT = "FOUND_INCORRECT_AMOUNT"
    FOUND_CORRECT_AMOUNT = "FOUND_CORRECT_AMOUNT"
    TIMEOUT = "TIMEOUT"

class TransactionMonitor:
    def __init__(self, rpc_url: str):
        logger.debug(f"[DEBUG] Initializing TransactionMonitor with rpc_url: {rpc_url}")
        logger.info("🚀 Initializing Transaction Monitor...")
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            logger.error("[ERROR] Failed to connect to Ethereum network")
            raise ValueError("Failed to connect to Ethereum network")
        logger.debug(f"[DEBUG] Web3 connected successfully, chain_id: {self.w3.eth.chain_id}")
        self.start_block_number = 0
        self.blocks_checked = 0
        self.is_destroyed = False
        self.found_transactions: List[Dict[str, str]] = []
        self._stop_event = asyncio.Event()
        logger.debug("[DEBUG] TransactionMonitor initialized")

    async def wait_for_confirmations(self, tx_hash: str, confirmations: int) -> Optional[Dict]:
        logger.debug(f"[DEBUG] Waiting for confirmations for tx_hash: {tx_hash}, confirmations: {confirmations}")
        try:
            # Get the transaction receipt
            receipt = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.w3.eth.get_transaction_receipt(tx_hash)
            )
            if not receipt:
                logger.debug("[DEBUG] No receipt found for tx_hash")
                return None

            # Get the transaction's block number
            tx_block = receipt["blockNumber"]
            logger.debug(f"[DEBUG] Transaction block number: {tx_block}")
            # Get the latest block number
            latest_block = await asyncio.get_event_loop().run_in_executor(
                None, self.w3.eth.get_block_number
            )
            logger.debug(f"[DEBUG] Latest block number: {latest_block}")

            # Check if enough confirmations have occurred
            if latest_block >= tx_block + confirmations - 1:
                logger.debug("[DEBUG] Enough confirmations reached")
                return receipt

            # Poll until enough confirmations are reached
            while latest_block < tx_block + confirmations - 1:
                await asyncio.sleep(5)  # Wait 5 seconds before checking again
                latest_block = await asyncio.get_event_loop().run_in_executor(
                    None, self.w3.eth.get_block_number
                )
                logger.debug(f"[DEBUG] Polling: {latest_block - tx_block + 1}/{confirmations} confirmations")

            logger.debug("[DEBUG] Confirmations completed")
            return receipt

        except Exception as e:
            logger.error(f"[ERROR] Error waiting for confirmations: {e}")
            return None

    async def monitor_transaction(self, sender_address: str) -> TransactionState:
        logger.info("📝 Validating inputs...")
        if not Web3.is_address(sender_address):
            logger.error("[ERROR] Invalid sender address format")
            raise ValueError("Invalid sender address format")

        criteria = {
            "recipient_address": config["recipient_address"],
            "sender_address": sender_address,
            "expected_amount": config["expected_amount"],
            "max_blocks_to_wait": config["max_blocks_to_wait"],
            "confirmations": config["confirmations"]
        }

        expected_amount_wei = Web3.to_wei(criteria["expected_amount"], "ether")
        logger.info(f"💰 Expected amount in Wei: {expected_amount_wei}")

        network = await asyncio.get_event_loop().run_in_executor(None, self.w3.eth.get_block, "latest")
        logger.info(f"🌐 Connected to network: {self.w3.eth.chain_id}")
        self.start_block_number = network["number"]
        logger.debug(f"[DEBUG] Starting block number set to: {self.start_block_number}")

        logger.info(
            f"🔍 Starting transaction monitoring:\n"
            f"   - Starting from block: {self.start_block_number}\n"
            f"   - Expected amount: {criteria['expected_amount']} ETH\n"
            f"   - From address: {criteria['sender_address']}\n"
            f"   - To address: {criteria['recipient_address']}\n"
            f"   - Will monitor for {criteria['max_blocks_to_wait']} blocks"
        )

        async def check_block(block_number: int) -> Optional[TransactionState]:
            logger.debug(f"[DEBUG] Checking block {block_number}")
            if self.is_destroyed or self._stop_event.is_set():
                logger.debug("[DEBUG] Monitor destroyed or stopped")
                return None

            try:
                block: BlockData = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.w3.eth.get_block(block_number, full_transactions=True)
                )
                if not block:
                    logger.debug("[DEBUG] No block data retrieved")
                    return None

                self.blocks_checked += 1
                logger.debug(f"[DEBUG] Blocks checked: {self.blocks_checked}/{criteria['max_blocks_to_wait']}")

                if self.blocks_checked > criteria["max_blocks_to_wait"]:
                    logger.info("⏰ Maximum block limit reached!")
                    if self.found_transactions:
                        logger.debug("[DEBUG] Found incorrect amount transactions")
                        for tx in self.found_transactions:
                            logger.debug(f"   Hash: {tx['hash']}, Amount: {tx['amount']} ETH")
                        return TransactionState.FOUND_INCORRECT_AMOUNT
                    logger.debug("[DEBUG] No transactions found, returning TIMEOUT")
                    return TransactionState.TIMEOUT

                if block.get("transactions"):
                    logger.debug(f"[DEBUG] Found {len(block['transactions'])} transactions in block {block_number}")
                    for tx in block["transactions"]:
                        if self.is_destroyed or self._stop_event.is_set():
                            logger.debug("[DEBUG] Monitor interrupted during transaction check")
                            return None

                        if (
                            tx["from"].lower() == criteria["sender_address"].lower() and
                            tx.get("to") and tx["to"].lower() == criteria["recipient_address"].lower()
                        ):
                            amount_in_eth = Web3.from_wei(tx["value"], "ether")
                            logger.debug(
                                f"[DEBUG] Found transaction: Hash={tx['hash']}, Amount={amount_in_eth} ETH"
                            )

                            if tx["value"] < expected_amount_wei:
                                logger.debug("[DEBUG] Transaction amount less than expected")
                                self.found_transactions.append({"hash": tx["hash"], "amount": str(amount_in_eth)})
                                continue

                            if tx["value"] >= expected_amount_wei:
                                logger.debug("[DEBUG] Transaction matches criteria, waiting for confirmations")
                                receipt = await self.wait_for_confirmations(tx["hash"], criteria["confirmations"])
                                if receipt:
                                    logger.debug("[DEBUG] Confirmation successful")
                                    return TransactionState.FOUND_CORRECT_AMOUNT
                                else:
                                    logger.debug("[DEBUG] Failed to get confirmation receipt")
                                    continue

                logger.debug("[DEBUG] No matching transactions in this block")
                return None

            except Exception as e:
                if not self.is_destroyed:
                    logger.error(f"[ERROR] Error processing block {block_number}: {e}")
                return None

        # Monitor new blocks
        current_block = self.start_block_number
        logger.debug(f"[DEBUG] Starting block monitoring loop at block {current_block}")
        while not self.is_destroyed and not self._stop_event.is_set():
            latest_block = await asyncio.get_event_loop().run_in_executor(None, self.w3.eth.get_block_number)
            logger.debug(f"[DEBUG] Latest block: {latest_block}")
            if latest_block > current_block:
                for block_number in range(current_block + 1, latest_block + 1):
                    logger.debug(f"[DEBUG] Processing block range: {block_number}")
                    result = await check_block(block_number)
                    if result:
                        logger.debug(f"[DEBUG] Block check returned: {result}")
                        self._stop_event.set()
                        return result
                current_block = latest_block
                logger.debug(f"[DEBUG] Updated current_block to: {current_block}")

            # Timeout mechanism
            if self.blocks_checked >= criteria["max_blocks_to_wait"]:
                logger.debug("[DEBUG] Timeout condition met")
                self._stop_event.set()
                return TransactionState.TIMEOUT if not self.found_transactions else TransactionState.FOUND_INCORRECT_AMOUNT

            logger.debug("[DEBUG] Sleeping for 5 seconds before next check")
            await asyncio.sleep(5)  # Check every 5 seconds

        logger.debug("[DEBUG] Monitor loop exited")
        return TransactionState.TIMEOUT

    async def destroy(self):
        logger.info("🧹 Cleaning up monitor resources...")
        self.is_destroyed = True
        self._stop_event.set()
        await asyncio.sleep(0.1)  # Allow pending tasks to complete
        logger.info("✅ Cleanup completed")