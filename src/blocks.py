from typing import Dict, Generator, List, Optional, Tuple
import dataclasses
import hashlib

import transactions as transacts


Hash = bytes


VERSION: int = 0

HASH_SIZE: int = 32
HEADER_SIZE: int = 101

REWARD_HASH: bytes = (0).to_bytes(HASH_SIZE, byteorder="big")
REWARD_SENDER: int = 0


@dataclasses.dataclass
class Header:
    """ """

    version: int
    previous_hash: Hash
    merkle_root: Hash
    timestamp: int
    nonce: int

    def encode(self):
        """ """
        return (
            self.version.to_bytes(1, byteorder="big")
            + self.previous_hash
            + self.merkle_root
            + self.timestamp.to_bytes(4, byteorder="big")
            + self.nonce.to_bytes(32, byteorder="big")
        )


def decode_header(header_bytes: bytes) -> Header:
    """ """
    version = header_bytes[0]
    previous_hash = header_bytes[1 : 1 + HASH_SIZE]
    merkle_root = header_bytes[1 + HASH_SIZE : 1 + HASH_SIZE + HASH_SIZE]
    timestamp = int.from_bytes(
        header_bytes[1 + HASH_SIZE + HASH_SIZE : 1 + HASH_SIZE + HASH_SIZE + 4],
        byteorder="big",
    )
    nonce = int.from_bytes(
        header_bytes[1 + HASH_SIZE + HASH_SIZE + 4 :], byteorder="big"
    )

    return Header(
        version=version,
        previous_hash=previous_hash,
        merkle_root=merkle_root,
        timestamp=timestamp,
        nonce=nonce,
    )


@dataclasses.dataclass
class Block:
    """ """

    header: Header
    transactions: List[transacts.Transaction]

    def encode(self):
        """ """
        header_bytes, transactions_bytes = self.header.encode(), b""

        for transaction in self.transactions:
            transactions_bytes += transaction.encode()

        transaction_counter_bytes = len(self.transactions).to_bytes(1, byteorder="big")
        block_size = (
            1
            + len(header_bytes)
            + len(transaction_counter_bytes)
            + len(transactions_bytes)
        )

        return (
            block_size.to_bytes(1, byteorder="big")
            + header_bytes
            + transaction_counter_bytes
            + transactions_bytes
        )


@dataclasses.dataclass
class Blockchain:
    """ """

    chain: List[Hash]
    blocks: Dict[Hash, Block]

    def encode(self):
        """ """
        blockchain_bytes = b""

        for block_hash in self.chain:
            blockchain_bytes += self.blocks[block_hash].encode()

        return blockchain_bytes


def iterate_message(message: bytes) -> Generator:
    """ """
    message_size = len(message)
    byte_index = 0

    while True:
        if byte_index == message_size:
            yield None, None

        block_size = message[byte_index]
        yield block_size, message[byte_index : byte_index + block_size]

        byte_index += block_size


def decode_message(message: bytes) -> Blockchain:
    """ """
    chain: List[Hash] = []
    blocks: Dict[Hash, Block] = {}

    for block_size, block_bytes in iterate_message(message):
        if block_size is None:
            break

        header_bytes = block_bytes[1 : 1 + HEADER_SIZE]
        transaction_counter = int.from_bytes(
            block_bytes[1 + HEADER_SIZE : 1 + HEADER_SIZE + 1], byteorder="big"
        )
        transactions_bytes = block_bytes[1 + HEADER_SIZE + 1 :]

        header = decode_header(header_bytes)
        transactions = transacts.decode_transactions(
            transaction_counter, transactions_bytes
        )

        block = Block(header=header, transactions=transactions)
        block_hash = hashlib.sha256(hashlib.sha256(header.encode()).digest()).digest()

        chain.append(block_hash)
        blocks[block_hash] = block

    return Blockchain(chain=chain, blocks=blocks)


def init_genesis_block() -> Block:
    """ """
    reward = transacts.Transaction(reference_hash=REWARD_HASH, sender=0, receiver=7000)
    transaction_hash = hashlib.sha256(reward.encode()).digest()
    merkle_tree = transacts.init_merkle_tree([transaction_hash])

    assert merkle_tree is not None
    merkle_root = merkle_tree.tree_hash

    previous_hash = (0).to_bytes(HASH_SIZE, byteorder="big")
    header = Header(
        version=VERSION,
        previous_hash=previous_hash,
        merkle_root=merkle_root,
        timestamp=1634700000,
        nonce=102275,
    )

    guess = hashlib.sha256(hashlib.sha256(header.encode()).digest())
    assert guess.hexdigest()[:4] == "0000"

    return Block(header=header, transactions=[reward])


def run_proof_of_work(
    previous_hash: Hash,
    merkle_root: Hash,
    timestamp: int,
    nonce: int = 0,
    iterations: Optional[int] = None,
) -> Tuple[bool, int, Optional[Hash], Optional[Header]]:
    """Find nonce that makes the first 4 bytes of twice-hashed header all zeroes. Maximum number of
    iterations can be specified."""
    iteration_counter = 0

    while True:
        if iterations is not None and iteration_counter == iterations:
            return False, nonce, None, None

        header = Header(
            version=VERSION,
            previous_hash=previous_hash,
            merkle_root=merkle_root,
            timestamp=timestamp,
            nonce=nonce,
        )
        guess = hashlib.sha256(hashlib.sha256(header.encode()).digest())

        if guess.hexdigest()[:4] == "0000":
            break

        nonce += 1
        iteration_counter += 1

    return True, nonce, guess.digest(), header


def validate_blockchain(
    blockchain: Blockchain, previous_hash: Optional[Hash] = None
) -> bool:
    """Check that all headers in the blockchain satisfy proof-of-work and indeed form a chain."""
    if previous_hash is None:
        previous_hash = (0).to_bytes(HASH_SIZE, byteorder="big")

    for block_hash in blockchain.chain:
        header = blockchain.blocks[block_hash].header

        if header.previous_hash != previous_hash:
            return False

        guess = hashlib.sha256(hashlib.sha256(header.encode()).digest())

        if guess.hexdigest()[:4] != "0000":
            return False

        previous_hash = guess.digest()

    return True


def replace_blockchain(
    current_blockchain: Blockchain, potential_blockchain: Blockchain
):
    """Compare blockchains and replace if potential blockchain is longer and valid."""
    if len(potential_blockchain.chain) < len(current_blockchain.chain):
        return False

    for i, block_hash in enumerate(potential_blockchain.chain):
        if not (
            i < len(current_blockchain.chain)
            and block_hash == current_blockchain.chain[i]
        ):
            break

        common_hash = block_hash

    remaining_blockchain = Blockchain(
        chain=potential_blockchain.chain[i:], blocks=potential_blockchain.blocks
    )

    return validate_blockchain(remaining_blockchain, common_hash)
