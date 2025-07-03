# Python Blockchain Implementation with LevelDB

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A complete blockchain implementation in Python using LevelDB for persistent storage, featuring:
- Cryptographic transactions with ECDSA
- Proof-of-Work mining
- Persistent blockchain storage
- Full chain validation

## Features

✔️ **Secure Transactions**  
✔️ **Persistent LevelDB Storage**  
✔️ **Proof-of-Work Consensus**  
✔️ **Chain Validation**  
✔️ **Customizable Mining Difficulty**  
✔️ **Transaction Signing & Verification**

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/python-blockchain.git
cd python-blockchain

2. Install dependencies:

```bash
pip install -U -r requirements.txt
```

## Requirements
+ Python 3.8+
+ plyvel (LevelDB bindings)
+ ecdsa (for cryptographic operations)

## Usage

Running the Blockchain

```python
from blockchain import Blockchain

# Initialize blockchain
blockchain = Blockchain()

# Create sample transaction
from ecdsa import SigningKey, SECP256k1
import binascii

priv_key = SigningKey.generate(curve=SECP256k1)
pub_key = priv_key.get_verifying_key()

tx = Transaction(
    sender_pubkey=binascii.hexlify(pub_key.to_string()).decode(),
    recipient_address="recipient_address_hex",
    amount=1.0
)
tx.sign(binascii.hexlify(priv_key.to_string()).decode())

# Add transaction and mine block
blockchain.add_transaction(tx)
blockchain.mine_block()

# Verify chain integrity
print("Chain valid:", blockchain.validate_chain())
```

##  Reference
`Blockchain` Class:
- `__init__(db_path='./blockchain_db')`: Initialize new or load existing blockchain

- `add_transaction(transaction)`: Add verified transaction to pending pool

- `mine_block()`: Mine new block with pending transactions

- `get_block(block_hash)`: Retrieve block by hash

- `get_last_block()`: Get most recent block

- `validate_chain()`: Validate entire blockchain integrity

`Transaction` Class:
- `sign(private_key_hex)`: Sign transaction with private key

- `verify()`: Verify transaction signature

## Database Structure

The LevelDB database stores:

+ Blocks by their hash (key: block_hash, value: block_data)

+ Last block hash (key: 'last_hash')

+ (Optional) UTXO set (for cryptocurrency implementations)