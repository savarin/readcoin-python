import binascii

import blocks


def test_proof_of_work():
    """ """
    previous_hash = (0).to_bytes(32, byteorder="big")
    timestamp = 1634700000

    is_new_block, nonce, current_hash, header = blocks.run_proof_of_work(
        previous_hash, timestamp, 0, 1000
    )

    assert not is_new_block
    assert nonce == 1000
    assert current_hash is None
    assert header is None

    is_new_block, nonce, current_hash, header = blocks.run_proof_of_work(
        previous_hash, timestamp, 70000, 1000
    )

    assert is_new_block
    assert nonce == 70822
    assert (
        binascii.hexlify(current_hash)
        == b"00001ff58495c3dc2a1aaa69ebca4e9b3e05e63e5a319fb73bcdccbcdbba1e72"
    )
    assert (
        binascii.hexlify(header)
        == b"000000000000000000000000000000000000000000000000000000000000000000616f8ae000000000000000000000000000000000000000000000000000000000000114a6"
    )

    previous_hash = current_hash
    timestamp = 1634700600

    is_new_block, nonce, current_hash, header = blocks.run_proof_of_work(
        previous_hash, timestamp, 0, 1000
    )

    assert not is_new_block
    assert nonce == 1000
    assert current_hash is None
    assert header is None

    is_new_block, nonce, current_hash, header = blocks.run_proof_of_work(
        previous_hash, timestamp, 58000, 1000
    )

    assert is_new_block
    assert nonce == 58768
    assert (
        binascii.hexlify(current_hash)
        == b"000071e6ff5b358e57339b42d45b20acc0f112c218fa435b3ffa8f239b777347"
    )
    assert (
        binascii.hexlify(header)
        == b"0000001ff58495c3dc2a1aaa69ebca4e9b3e05e63e5a319fb73bcdccbcdbba1e72616f8d38000000000000000000000000000000000000000000000000000000000000e590"
    )


def test_validate_blockchain():
    """ """
    _, blockchain = blocks.init_genesis_block()
    transaction_counter, transactions = blocks.init_transactions(7000)

    is_new_block, block_counter, current_hash, _ = blocks.validate_blockchain(
        blockchain
    )

    assert is_new_block
    assert block_counter == 1
    assert (
        binascii.hexlify(current_hash)
        == b"00001ff58495c3dc2a1aaa69ebca4e9b3e05e63e5a319fb73bcdccbcdbba1e72"
    )

    previous_hash = current_hash
    timestamp = 1634700600

    _, _, _, header = blocks.run_proof_of_work(previous_hash, timestamp, 58000, 1000)
    block = blocks.init_block(header, transaction_counter, transactions)
    blockchain += block

    is_new_block, block_counter, current_hash, block = blocks.validate_blockchain(
        blockchain
    )

    assert is_new_block
    assert block_counter == 2
    assert (
        binascii.hexlify(current_hash)
        == b"000071e6ff5b358e57339b42d45b20acc0f112c218fa435b3ffa8f239b777347"
    )

    header = (0).to_bytes(32, byteorder="big")
    block = blocks.init_block(header, transaction_counter, transactions)
    blockchain += block

    is_new_block, block_counter, current_hash, _ = blocks.validate_blockchain(
        blockchain
    )

    assert not is_new_block
    assert block_counter == 3
    assert current_hash is None


def test_validate_transactions():
    """ """
    _, blockchain = blocks.init_genesis_block()
    transaction_counter, transactions = blocks.init_transactions(7000)

    _, _, previous_hash, _ = blocks.validate_blockchain(blockchain)
    _, _, _, header = blocks.run_proof_of_work(previous_hash, 1634700600, 58000, 1000)
    block = blocks.init_block(header, transaction_counter + 1, transactions)

    reference_hash = previous_hash
    sender = (7000).to_bytes(2, byteorder="big")
    receiver = (8000).to_bytes(2, byteorder="big")
    transfer = reference_hash + sender + receiver

    block += transfer
    block = (block[0] + len(transfer)).to_bytes(1, byteorder="big") + block[1:]
    blockchain += block

    current_transaction_counter = int.from_bytes(
        block[1 + blocks.HEADER_SIZE : 1 + blocks.HEADER_SIZE + 1], byteorder="big"
    )
    current_transactions = block[1 + blocks.HEADER_SIZE + 1 :]

    is_valid_transaction = blocks.validate_transactions(
        blockchain, current_transactions, current_transaction_counter
    )

    assert is_valid_transaction

    _, _, previous_hash, _ = blocks.validate_blockchain(blockchain)
    _, _, _, header = blocks.run_proof_of_work(previous_hash, 1634701200, 3800, 1000)
    block = blocks.init_block(header, transaction_counter + 1, transactions)

    block += transfer
    block = (block[0] + len(transfer)).to_bytes(1, byteorder="big") + block[1:]
    blockchain += block

    current_transaction_counter = (
        int.from_bytes(
            block[1 + blocks.HEADER_SIZE : 1 + blocks.HEADER_SIZE + 1], byteorder="big"
        )
        + 1
    )
    current_transactions = block[1 + blocks.HEADER_SIZE + 1 :]

    is_valid_transaction = blocks.validate_transactions(
        blockchain, current_transactions, current_transaction_counter
    )

    assert not is_valid_transaction
