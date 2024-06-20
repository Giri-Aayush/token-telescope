from flask import Flask, request, jsonify
from web3 import Web3
import rlp
from supabase import create_client, Client
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

# Supabase configuration
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')
print(supabase_url, supabase_key)
supabase: Client = create_client(supabase_url, supabase_key)
# Web3 configuration
alchemy_api_key = os.environ.get('ALCHEMY_API_KEY')
web3 = Web3(Web3.HTTPProvider(f'https://eth-mainnet.g.alchemy.com/v2/{alchemy_api_key}'))

def mk_contract_address(sender, nonce):
    return Web3.keccak(rlp.encode([Web3.to_bytes(hexstr=sender), nonce]))[12:]

def get_contract_address(sender, nonce):
    contract_address = mk_contract_address(sender, nonce)
    return Web3.to_checksum_address(contract_address)

@app.route('/predict', methods=['POST'])
def predict_contract_address():
    try:
        print(f"Content-Type: {request.content_type}")
        print(f"Request data: {request.data}")

        if request.content_type != 'application/json':
            return jsonify({'error': "Unsupported Media Type: Content-Type must be 'application/json'"}), 415

        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Invalid JSON'}), 400

        print(f"Parsed JSON data: {data}")

        contract_address = data.get('contractAddress')
        nonce = data.get('nonce')

        if not contract_address:
            return jsonify({'error': 'Missing contractAddress parameter'}), 400

        print(f"Contract Address: {contract_address}")
        print(f"Nonce: {nonce}")

        # Get the current block number
        block_number = web3.eth.block_number

        if nonce is not None:
            nonce = int(nonce)
            # Predict the contract address for the specified nonce
            predicted_address = get_contract_address(contract_address, nonce)
        else:
            # Get the current nonce for the contract address
            current_nonce = web3.eth.get_transaction_count(contract_address)
            # Predict the contract address for the next nonce (automatic nonce detection)
            predicted_address = get_contract_address(contract_address, current_nonce)

        print(f"Predicted Address: {predicted_address}")

        # Get the current timestamp
        timestamp = datetime.datetime.now().isoformat()

        # Get the balance of the contract address
        balance = web3.eth.get_balance(contract_address)
        balance_in_eth = web3.from_wei(balance, 'ether')

        print(f"Balance in ETH: {balance_in_eth}")

        if balance_in_eth > 1.5:
            # Insert the data into the Supabase table only if balance is greater than 1.5 ETH
            data = {
                'contract_address': contract_address,
                'predicted_address': predicted_address,
                'block_number': block_number,
                'timestamp': timestamp,
                'nonce': nonce if nonce is not None else current_nonce,
                'balance': float(balance_in_eth)  # Convert balance to float
            }
            print(data)
            response = supabase.table('Public Keys').insert(data).execute()
            print(f"Supabase insert response: {response}")

        return jsonify({'predictedAddress': predicted_address, 'balance': float(balance_in_eth)})  # Convert balance to float

    except Exception as e:
        print(f"Error in /predict endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'Server is running'}), 200

if __name__ == '__main__':
    app.run(port=5000)
