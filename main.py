import hashlib
import json
from time import time
from dataclasses import dataclass
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import binascii


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
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4
        self.pending_transactions = []

    def create_genesis_block(self):
        genesis_tx = Transaction(sender_pubkey="0", recipient_address="0", amount=0)
        return Block(0, time(), [genesis_tx], "0")

    def add_transaction(self, transaction):
        # self.pending_transactions.append(transaction)
        """Add a new transaction if it's properly signed"""
        if not transaction.verify():
            raise ValueError("Invalid transaction signature")
        self.pending_transactions.append(transaction)

    def mine_block(self):
        if not self.pending_transactions:
            print("No transxtions to mine!")
            return None

        last_block = self.chain[-1]

        new_block = Block(
            index=last_block.index + 1,
            timestamp=time(),
            transactions=self.pending_transactions,
            previous_hash=last_block.hash,
        )

        # Perform the proof-of-work
        print(f"Mining block {new_block.index}...")
        mined_block = proof_of_work(new_block, self.difficulty)

        self.chain.append(mined_block)
        self.pending_transactions = []
        print(f"Block mined: {mined_block.hash}")
        return mined_block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Check hash integrity
            if current.hash != current.calculate_hash():
                return False

            # Check hash meets difficulty requirement
            if not current.hash.startswith("0" * self.difficulty):
                return False

            # Check chain linkage
            if current.previous_hash != previous.hash:
                return False

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
    print("\nBlockchain valied?", blockchain.is_chain_valid())

    # Try tempering (this will invalidate the chain)
    print("\nAttempting to temper with block 1...")
    # blockchain.chain[1].transactions = ["Hacker sends 100 BTC to themselves"]
    # print("Blockchain valid after tempering?", blockchain.is_chain_valid())
