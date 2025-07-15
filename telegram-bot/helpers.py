from web3 import Web3
import rlp

def predict_contract_address(sender: str, nonce: int) -> str:
    encoded = Web3.keccak(rlp.encode([Web3.to_bytes(hexstr=sender), nonce]))[12:]
    return Web3.to_checksum_address(encoded)
