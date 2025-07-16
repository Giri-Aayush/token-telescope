import asyncio
from web3 import Web3
from web3.types import BlockData
from typing import List, Dict, Optional
from config import config
from constants import TransactionState
import logging

logger = logging.getLogger(__name__)

class TransactionMonitor:
    def __init__(self, rpc_url: str):
        logger.info("🚀 Initializing Transaction Monitor...")
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not self.w3.is_connected():
            logger.error("Failed to connect to Ethereum network")
            raise ValueError("Failed to connect to Ethereum network")
            
        self.start_block_number = 0
        self.blocks_checked = 0
        self.is_destroyed = False
        self.found_transactions: List[Dict[str, str]] = []
        self._stop_event = asyncio.Event()
        logger.info(f"Connected to network: {self.w3.eth.chain_id}")

    async def wait_for_confirmations(self, tx_hash: str, confirmations: int) -> Optional[Dict]:
        try:
            receipt = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.w3.eth.get_transaction_receipt(tx_hash)
            )
            
            if not receipt:
                return None

            tx_block = receipt["blockNumber"]
            
            while True:
                latest_block = await asyncio.get_event_loop().run_in_executor(
                    None, self.w3.eth.get_block_number
                )
                
                if latest_block >= tx_block + confirmations - 1:
                    logger.info(f"Transaction {tx_hash} confirmed with {confirmations} confirmations")
                    return receipt
                    
                logger.debug(f"Waiting for confirmations: {latest_block - tx_block + 1}/{confirmations}")
                await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"Error waiting for confirmations: {e}")
            return None

    async def monitor_transaction(self, sender_address: str) -> TransactionState:
        if not Web3.is_address(sender_address):
            raise ValueError("Invalid sender address format")

        expected_amount_wei = Web3.to_wei(config.EXPECTED_AMOUNT, "ether")
        network_block = await asyncio.get_event_loop().run_in_executor(
            None, self.w3.eth.get_block, "latest"
        )
        self.start_block_number = network_block["number"]

        logger.info(
            f"🔍 Starting transaction monitoring:\n"
            f"   - Starting from block: {self.start_block_number}\n"
            f"   - Expected amount: {config.EXPECTED_AMOUNT} ETH\n"
            f"   - From: {sender_address}\n"
            f"   - To: {config.RECIPIENT_ADDRESS}\n"
            f"   - Max blocks: {config.MAX_BLOCKS_TO_WAIT}"
        )

        current_block = self.start_block_number

        while not self.is_destroyed and not self._stop_event.is_set():
            latest_block = await asyncio.get_event_loop().run_in_executor(
                None, self.w3.eth.get_block_number
            )

            if latest_block > current_block:
                for block_number in range(current_block + 1, latest_block + 1):
                    result = await self._check_block(
                        block_number, sender_address, expected_amount_wei
                    )
                    if result:
                        self._stop_event.set()
                        return result
                current_block = latest_block

            if self.blocks_checked >= config.MAX_BLOCKS_TO_WAIT:
                self._stop_event.set()
                return (TransactionState.FOUND_INCORRECT_AMOUNT 
                       if self.found_transactions 
                       else TransactionState.TIMEOUT)

            await asyncio.sleep(5)

        return TransactionState.TIMEOUT

    async def _check_block(self, block_number: int, sender_address: str, 
                          expected_amount_wei: int) -> Optional[TransactionState]:
        if self.is_destroyed or self._stop_event.is_set():
            return None

        try:
            block: BlockData = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.w3.eth.get_block(block_number, full_transactions=True)
            )

            if not block:
                return None

            self.blocks_checked += 1
            logger.debug(f"Checked block {block_number} ({self.blocks_checked}/{config.MAX_BLOCKS_TO_WAIT})")

            if self.blocks_checked > config.MAX_BLOCKS_TO_WAIT:
                return (TransactionState.FOUND_INCORRECT_AMOUNT 
                       if self.found_transactions 
                       else TransactionState.TIMEOUT)

            if not block.get("transactions"):
                return None

            for tx in block["transactions"]:
                if self._is_target_transaction(tx, sender_address):
                    amount_in_eth = Web3.from_wei(tx["value"], "ether")
                    
                    if tx["value"] < expected_amount_wei:
                        self.found_transactions.append({
                            "hash": tx["hash"], 
                            "amount": str(amount_in_eth)
                        })
                        continue

                    if tx["value"] >= expected_amount_wei:
                        receipt = await self.wait_for_confirmations(
                            tx["hash"], config.CONFIRMATIONS
                        )
                        if receipt:
                            logger.info(f"✅ Found valid transaction: {tx['hash']}")
                            return TransactionState.FOUND_CORRECT_AMOUNT

            return None

        except Exception as e:
            if not self.is_destroyed:
                logger.error(f"Error processing block {block_number}: {e}")
            return None

    def _is_target_transaction(self, tx, sender_address: str) -> bool:
        return (tx["from"].lower() == sender_address.lower() and
                tx.get("to") and 
                tx["to"].lower() == config.RECIPIENT_ADDRESS.lower())

    async def destroy(self):
        logger.info("🧹 Cleaning up monitor resources...")
        self.is_destroyed = True
        self._stop_event.set()
        await asyncio.sleep(0.1)
        logger.info("✅ Cleanup completed")