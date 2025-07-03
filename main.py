import hashlib
import json
from time import time
from dataclasses import dataclass, asdict
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import binascii
import plyvel
from pathlib import Path


@dataclass
class Transaction:
    sender_pubkey: str  # Stored as hex string
    recipient_address: str
    amount: float
    signature: str = None

    def sign(self, private_key_hex):
        """Sign the transaction with sender's private key"""
        private_key = SigningKey.from_string(
            binascii.unhexlify(private_key_hex), curve=SECP256k1
        )
        tx_data = self._get_data_to_sign()
        signature = private_key.sign(tx_data)
        self.signature = binascii.hexlify(signature).decode()

    def verify(self):
        """Verify the transaction signature"""
        if not self.signature:
            return False
        try:
            pub_key = VerifyingKey.from_string(
                binascii.unhexlify(self.sender_pubkey), curve=SECP256k1
            )
            return pub_key.verify(
                binascii.unhexlify(self.signature), self._get_data_to_sign()
            )
        except:
            return False

    def _get_data_to_sign(self):
        """Data that gets signed (excludes the signature itself)"""
        return json.dumps(
            {
                "sender": self.sender_pubkey,
                "recipient": self.recipient_address,
                "amount": self.amount,
            }
        ).encode()


@dataclass
class Block:
    index: int
    timestamp: float
    transactions: list[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: str = None

    def calculate_hash(self):
        block_string = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "transactions": [tx.__dict__ for tx in self.transactions],
                "previous_hash": self.previous_hash,
                "nonce": self.nonce,
            },
            sort_keys=True,
        ).encode()
        return hashlib.sha256(block_string).hexdigest()


def proof_of_work(block, difficulty=4):
    """
    Simple Proof-of-work algoritm:
    - Find a nonce that make the hash start with difficulty zeros
    """
    prefix = "0" * difficulty
    block.nonce = 0

    while True:
        block.hash = block.calculate_hash()
        if block.hash.startswith(prefix):
            return block
        block.nonce += 1


class Blockchain:
    def __init__(self, db_path="./blockchain_db"):
        self.db = plyvel.DB(db_path, create_if_missing=True)
        self.difficulty = 4
        self.pending_transactions = []

        if not self.db.get(b"last_hash"):
            self._create_genesis_block

    def _create_genesis_block(self):
        genesis_tx = Transaction(sender_pubkey="0", recipient_address="0", amount=0)
        genesis_block = Block(
            index=0, timestamp=time(), transactions=[genesis_tx], previous_hash="0"
        )
        genesis_block.hash = genesis_block.calculate_hash()
        self._save_block(genesis_block)

    def _save_block(self, block):
        # Save block to LevelDB
        block_data = json.dumps(asdict(block)).encode()
        self.db.put(block.hash.encode(), block_data)
        self.db.put(b"last_path", block.hash.encode())

    def get_last_block(self):
        last_hash = self.db.get(b"last_hash")
        if not last_hash:
            return None
        block_data = json.loads(self.db.get(last_hash))
        return self._deserialize_block(block_data)

    def _deserialize_block(self, block_data):
        transactions = [Transaction(**tx) for tx in block_data["transactions"]]
        return Block(
            index=block_data["index"],
            timestamp=block_data["timestamp"],
            transactions=transactions,
            previous_hash=block_data["previous_hash"],
            nonce=block_data["nonce"],
            hash=block_data["hash"],
        )

    def add_transaction(self, transaction):
        """Add a new transaction if it's properly signed"""
        if not transaction.verify():
            raise ValueError("Invalid transaction signature")
        self.pending_transactions.append(transaction)

    def mine_block(self):
        if not self.pending_transactions:
            print("No transxtions to mine!")
            return None

        last_block = self.get_last_block()

        new_block = Block(
            index=last_block.index + 1,
            timestamp=time(),
            transactions=self.pending_transactions,
            previous_hash=last_block.hash,
        )

        # Perform the proof-of-work
        print(f"Mining block {new_block.index}...")
        prefix = "0" * self.difficulty
        while True:
            new_block.hash = new_block.calculate_hash()
            if new_block.hash.startswith(prefix):
                break
            new_block.nonce += 1

        self._save_block(new_block)
        self.pending_transactions = []
        print(f"Block mined: {new_block.hash}")
        return new_block

    def get_block(self, block_hash):
        block_data = self.db.get(block_hash.encode())
        if block_data:
            return self._deserialize_block(json.loads(block_data))
        return None

    def validate_chain(self):
        current_hash = self.db.get(b"last_hash")
        while current_hash:
            block = self.get_block(current_hash.decode())
            if not block:
                return False

            # Validate hash
            if block.hash != block.calculate_hash():
                return False

            # Validate previous hash line
            if block.index > 0:
                prev_block = self.get_block(block.previous_hash)
                if not prev_block or prev_block.index != block.index - 1:
                    return False

            current_hash = block.previous_hash.encode()
        return True


# Usage
if __name__ == "__main__":
    hojat_priv_key = SigningKey.generate(curve=SECP256k1)
    hojat_priv_key_hex = binascii.hexlify(hojat_priv_key.to_string()).decode()
    hojat_pub_key_hex = binascii.hexlify(
        hojat_priv_key.get_verifying_key().to_string()
    ).decode()

    ehsan_priv_key = SigningKey.generate(curve=SECP256k1)
    ehsan_priv_key_hex = binascii.hexlify(hojat_priv_key.to_string()).decode()
    ehsan_pub_key_hex = binascii.hexlify(
        hojat_priv_key.get_verifying_key().to_string()
    ).decode()

    blockchain = Blockchain()

    tx = Transaction(
        sender_pubkey=hojat_pub_key_hex, recipient_address=ehsan_pub_key_hex, amount=1.5
    )
    tx.sign(hojat_priv_key_hex)

    # Add some transactions
    print(f"{tx.sender_pubkey} is sending {tx.amount} to {tx.recipient_address}")
    blockchain.add_transaction(tx)

    tx1 = Transaction(
        sender_pubkey=ehsan_pub_key_hex,
        recipient_address=hojat_pub_key_hex,
        amount=2.3,
    )
    tx1.sign(ehsan_priv_key_hex)

    print(f"{tx1.sender_pubkey} is sending {tx1.amount} to {tx1.recipient_address}")
    blockchain.add_transaction(tx1)

    # Mine the block (This will take some time due to PoW)
    blockchain.mine_block()

    # Mine another block
    blockchain.mine_block()

    # Print the blockchain
    print("\nBlockchain:")
    for block in blockchain.chain:
        print(f"\nBlock #{block.index}:")
        print(f"Hash: {block.hash}")
        print(f"Previous Hash: {block.previous_hash}")
        print(f"Nonce: {block.nonce}")
        print(f"Transactions:")
        for tx in block.transactions:
            print(
                f" {tx.sender_pubkey[:10]}... -> {tx.recipient_address[:10]}...: {tx.amount}"
            )

    # Validate the chain
    print("\nBlockchain valied?", blockchain.validate_chain())

    # Try tempering (this will invalidate the chain)
    print("\nAttempting to temper with block 1...")
    # blockchain.chain[1].transactions = ["Hacker sends 100 BTC to themselves"]
    # print("Blockchain valid after tempering?", blockchain.is_chain_valid())
