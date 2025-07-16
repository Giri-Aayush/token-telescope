import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MAINNET_RPC_URL = os.getenv("MAINNET_RPC_URL", "https://mainnet.infura.io/v3/111dffff7e304bb6ac87dfa3eedda096")
    SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL", "https://sepolia.infura.io/v3/111dffff7e304bb6ac87dfa3eedda096")
    RECIPIENT_ADDRESS = os.getenv("RECIPIENT_ADDRESS", "0x2650e3934F9AA7a3f9E8a5E9c2404Cc628674346")
    EXPECTED_AMOUNT = float(os.getenv("EXPECTED_AMOUNT", "0.01"))
    MAX_BLOCKS_TO_WAIT = int(os.getenv("MAX_BLOCKS_TO_WAIT", "100"))
    CONFIRMATIONS = int(os.getenv("CONFIRMATIONS", "3"))
    
    def __init__(self):
        self.current_network = "mainnet"
        self._rpc_url = self.MAINNET_RPC_URL
    
    @property
    def rpc_url(self):
        return self._rpc_url
    
    def toggle_network(self):
        if self.current_network == "mainnet":
            self.current_network = "sepolia"
            self._rpc_url = self.SEPOLIA_RPC_URL
        else:
            self.current_network = "mainnet"
            self._rpc_url = self.MAINNET_RPC_URL
        return self.current_network
    
    def get_network_indicator(self):
        return "🟢 Mainnet" if self.current_network == "mainnet" else "🔴 Sepolia"

config = Config()