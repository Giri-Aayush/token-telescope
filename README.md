# token-telescope
Warmachinerox@123

CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    contract_address TEXT NOT NULL,
    predicted_address TEXT NOT NULL,
    block_number INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    nonce INTEGER,
    balance NUMERIC
);