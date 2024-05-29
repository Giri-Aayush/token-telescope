from flask import Flask, request, jsonify
from web3 import Web3
import rlp
from supabase import create_client, Client
import datetime

app = Flask(__name__)

# Supabase configuration
supabase_url = 'https://mxhuvibqbrmyyksiuzcr.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14aHV2aWJxYnJteXlrc2l1emNyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTY5ODI3NjAsImV4cCI6MjAzMjU1ODc2MH0.f5wCBeFIKU2v04T1CVw6X3sgqiazkk0xRZZI-yAq2T8'
supabase: Client = create_client(supabase_url, supabase_key)

# Web3 configuration
web3 = Web3(Web3.HTTPProvider('https://eth-mainnet.g.alchemy.com/v2/IJbweBVOnwnTeoaIg10-jGVFe8aPfaH5'))

def mk_contract_address(sender, nonce):
    return Web3.keccak(rlp.encode([Web3.to_bytes(hexstr=sender), nonce]))[12:]

def get_contract_address(sender, nonce):
    contract_address = mk_contract_address(sender, nonce)
    return Web3.to_checksum_address(contract_address)

@app.route('/predict', methods=['POST'])
def predict_contract_address():
    try:
        data = request.get_json()
        contract_address = data.get('contractAddress')
        nonce = data.get('nonce')

        if not contract_address:
            return jsonify({'error': 'Missing contractAddress parameter'}), 400

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

        # Get the current timestamp
        timestamp = datetime.datetime.now().isoformat()

        # Get the balance of the contract address
        balance = web3.eth.get_balance(contract_address)
        balance_in_eth = web3.from_wei(balance, 'ether')

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
            supabase.table('predictions').insert(data).execute()

        return jsonify({'predictedAddress': predicted_address, 'balance': float(balance_in_eth)})  # Convert balance to float

    except Exception as e:
        print(f"Error in /predict endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(port=3000)