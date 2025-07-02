import hashlib
import json
from time import time
from dataclasses import dataclass


@dataclass
class Block:
    index: int
    timestamp: float
    transactions: list
    previous_hash: str
    nonce: int = 0
    hash: str = None

    def calculate_hash(self):
        block_string = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "transaction": self.transactions,
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
        return Block(0, time(), ["Genesis Block"], "0")

    def add_transaction(self, transaction):
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
    blockchain = Blockchain()

    # Add some transactions
    blockchain.add_transaction("Kian sends 1 BTC to Fateme")
    blockchain.add_transaction("Ehsan sends 0.5 BTC to Fateme")

    # Mine the block (This will take some time due to PoW)
    blockchain.mine_block()

    # Add more transaction
    blockchain.add_transaction("Hojat sends 0.1 BTC to Ehsan")
    blockchain.add_transaction("Omid sends 2 BTC to Pouria")

    # Mine another block
    blockchain.mine_block()

    # Print the blockchain
    print("\nBlockchain:")
    for block in blockchain.chain:
        print(f"\nBlock #{block.index}:")
        print(f"Hash: {block.hash}")
        print(f"Previous Hash: {block.previous_hash}")
        print(f"Nonce: {block.nonce}")
        print(f"Transactions: {block.transactions}")

    # Validate the chain
    print("\nBlockchain valied?", blockchain.is_chain_valid())

    # Try tempering (this will invalidate the chain)
    print("\nAttempting to temper with block 1...")
    blockchain.chain[1].transactions = ["Hacker sends 100 BTC to themselves"]
    print("Blockchain valid after tempering?", blockchain.is_chain_valid())
