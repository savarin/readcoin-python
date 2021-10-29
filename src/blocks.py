from typing import Generator, Optional, Tuple
import hashlib


VERSION: int = 0

HEADER_SIZE: int = 69
HASH_SIZE: int = 32

REWARD_HASH: bytes = (0).to_bytes(HASH_SIZE, byteorder="big")
REWARD_SENDER: bytes = (0).to_bytes(2, byteorder="big")


def init_header(previous_hash: bytes, timestamp: int, nonce: int) -> bytes:
    """ """
    return (
        VERSION.to_bytes(1, byteorder="big")
        + previous_hash
        + timestamp.to_bytes(4, byteorder="big")
        + nonce.to_bytes(32, byteorder="big")
    )


def init_transactions(node_port: int):
    """ """
    transaction_counter = 1
    transactions = REWARD_HASH + REWARD_SENDER + node_port.to_bytes(2, byteorder="big")

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


def init_genesis_block() -> Tuple[bytes, bytes]:
    """ """
    previous_hash = (0).to_bytes(HASH_SIZE, byteorder="big")
    timestamp = 1634700000
    nonce = 70822

    header = init_header(previous_hash, timestamp, nonce)
    guess = hashlib.sha256(hashlib.sha256(header).digest())
    assert guess.hexdigest()[:4] == "0000"

    transaction_counter, transactions = init_transactions(7000)
    block = init_block(header, transaction_counter, transactions)

    return guess.digest(), block


def run_proof_of_work(
    previous_hash: bytes,
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
    """ """
    block_counter = 0

    while True:
        block_size = blockchain[byte_index]
        block = blockchain[byte_index : byte_index + block_size]

        byte_index += block_size
        block_counter += 1

        yield block, block_counter, byte_index


def validate_blockchain(
    blockchain: bytes,
) -> Tuple[bool, int, Optional[bytes], Optional[bytes]]:
    """Check that all headers in the blockchain satisfy proof-of-work and indeed form a chain."""
    previous_hash = (0).to_bytes(HASH_SIZE, byteorder="big")
    blockchain_size = len(blockchain)

    for block, block_counter, byte_index in iterate_blockchain(
        blockchain, byte_index=0
    ):
        header = block[1 : 1 + HEADER_SIZE]

        if header[1:33] != previous_hash:
            return False, block_counter, None, None

        guess = hashlib.sha256(hashlib.sha256(header).digest())

        if guess.hexdigest()[:4] != "0000":
            return False, block_counter, None, None

        previous_hash = guess.digest()

        if byte_index == blockchain_size:
            break

    return True, block_counter, previous_hash, block


def iterate_transactions(transactions: bytes, transaction_counter: int) -> Generator:
    """ """
    transaction_size = HASH_SIZE + 2 + 2

    for i in range(transaction_counter):
        yield transactions[i * transaction_size : (i + 1) * transaction_size], i


def validate_transaction(
    blockchain: bytes, reference_hash: bytes, sender: bytes
) -> bool:
    """ """
    blockchain_size = len(blockchain)

    is_valid_reference = False

    for block, _, byte_index in iterate_blockchain(blockchain, byte_index=0):
        header = block[1 : 1 + HEADER_SIZE]
        guess = hashlib.sha256(hashlib.sha256(header).digest())

        if guess.digest() == reference_hash:
            is_valid_reference = True
            break

        if byte_index == blockchain_size:
            break

    if not is_valid_reference:
        return False

    transaction_counter = int.from_bytes(
        block[1 + HEADER_SIZE : 1 + HEADER_SIZE + 1], byteorder="big"
    )
    transactions = block[1 + HEADER_SIZE + 1 :]
    is_valid_input = False

    for transaction, _ in iterate_transactions(transactions, transaction_counter):
        receiver = transaction[HASH_SIZE + 2 : HASH_SIZE + 4]

        if receiver == sender:
            is_valid_input = True
            break

    if not is_valid_input:
        return False

    current_transaction_counter = 0

    for block, _, byte_index in iterate_blockchain(blockchain, byte_index=byte_index):
        transaction_counter = int.from_bytes(
            block[1 + HEADER_SIZE : 1 + HEADER_SIZE + 1], byteorder="big"
        )
        transactions = block[1 + HEADER_SIZE + 1 :]

        for transaction, transaction_number in iterate_transactions(
            transactions, transaction_counter
        ):
            if transaction_number == 0:
                continue

            current_reference_hash = transaction[:HASH_SIZE]
            current_sender = transaction[HASH_SIZE : HASH_SIZE + 2]

            if current_reference_hash == reference_hash and current_sender == sender:
                current_transaction_counter += 1

        if byte_index == blockchain_size:
            break

    return current_transaction_counter == 1


def validate_transactions(
    blockchain: bytes, transactions: bytes, transaction_counter: int
) -> bool:
    """ """
    for transaction, transaction_number in iterate_transactions(
        transactions, transaction_counter
    ):
        reference_hash = transaction[:HASH_SIZE]
        sender = transaction[HASH_SIZE : HASH_SIZE + 2]

        if transaction_number == 0:
            if not (reference_hash == REWARD_HASH and sender == REWARD_SENDER):
                return False

            continue

        if not validate_transaction(blockchain, reference_hash, sender):
            return False

    return True
