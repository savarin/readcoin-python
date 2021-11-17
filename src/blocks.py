from typing import Generator, Optional, Tuple
import hashlib


Hash = bytes


VERSION: int = 0
HEADER_SIZE: int = 69


def init_header(previous_hash: Hash, timestamp: int, nonce: int) -> bytes:
    """ """
    return (
        VERSION.to_bytes(1, byteorder="big")
        + previous_hash
        + timestamp.to_bytes(4, byteorder="big")
        + nonce.to_bytes(32, byteorder="big")
    )


def init_transactions(node_port: int):
    """ """
    sender = (0).to_bytes(2, byteorder="big")
    receiver = node_port.to_bytes(2, byteorder="big")

    transaction_counter = 1
    transactions = sender + receiver

    return transaction_counter, transactions


def init_block(header: bytes, transaction_counter: int, transactions: bytes) -> bytes:
    """ """
    block_size = 1 + HEADER_SIZE + 1 + len(transactions)

    return (
        block_size.to_bytes(1, byteorder="big")
        + header
        + transaction_counter.to_bytes(1, byteorder="big")
        + transactions
    )


def init_genesis_block() -> Tuple[Hash, bytes]:
    """ """
    previous_hash = (0).to_bytes(32, byteorder="big")
    timestamp = 1634700000
    nonce = 70822

    header = init_header(previous_hash, timestamp, nonce)
    guess = hashlib.sha256(hashlib.sha256(header).digest())
    assert guess.hexdigest()[:4] == "0000"

    transaction_counter, transactions = init_transactions(7000)
    block = init_block(header, transaction_counter, transactions)

    return guess.digest(), block


def run_proof_of_work(
    previous_hash: Hash,
    timestamp: int,
    nonce: int = 0,
    iterations: Optional[int] = None,
) -> Tuple[bool, int, Optional[bytes], Optional[bytes]]:
    """Find nonce that makes the first 4 bytes of twice-hashed header all zeroes. Maximum number of
    iterations can be specified."""
    iteration_counter = 0

    while True:
        if iterations is not None and iteration_counter == iterations:
            return False, nonce, None, None

        header = init_header(previous_hash, timestamp, nonce)
        guess = hashlib.sha256(hashlib.sha256(header).digest())

        if guess.hexdigest()[:4] == "0000":
            break

        nonce += 1
        iteration_counter += 1

    return True, nonce, guess.digest(), header


def iterate_blockchain(blockchain: bytes, byte_index: int = 0) -> Generator:
    """Helper function to simplify iterating through blocks in the blockchain."""
    blockchain_counter = 0

    while True:
        block_size = blockchain[byte_index]
        block = blockchain[byte_index : byte_index + block_size]

        byte_index += block_size
        blockchain_counter += 1

        yield block, blockchain_counter, byte_index


def validate_blockchain(blockchain: bytes) -> Tuple[bool, int, Optional[bytes]]:
    """Check that all headers in the blockchain satisfy proof-of-work and indeed form a chain."""
    previous_hash = (0).to_bytes(32, byteorder="big")
    blockchain_size = len(blockchain)

    for block, blockchain_counter, byte_index in iterate_blockchain(
        blockchain, byte_index=0
    ):
        header = block[1 : 1 + HEADER_SIZE]

        if header[1:33] != previous_hash:
            return False, blockchain_counter, None

        guess = hashlib.sha256(hashlib.sha256(header).digest())

        if guess.hexdigest()[:4] != "0000":
            return False, blockchain_counter, None

        previous_hash = guess.digest()

        if byte_index == blockchain_size:
            break

    return True, blockchain_counter, previous_hash
