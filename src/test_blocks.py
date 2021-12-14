import hashlib

import pytest

import blocks
import transactions as transacts


@pytest.fixture
def reward() -> transacts.Transaction:
    """ """
    return transacts.Transaction(
        reference_hash=blocks.REWARD_HASH, sender=blocks.REWARD_SENDER, receiver=7000
    )


@pytest.fixture
def transfer(reward) -> transacts.Transaction:
    """ """
    reference_hash = hashlib.sha256(reward.encode()).digest()

    return transacts.Transaction(
        reference_hash=reference_hash, sender=7000, receiver=8000
    )


@pytest.fixture
def merkle_root_with_1_transaction(reward) -> blocks.Hash:
    """ """
    merkle_tree = transacts.init_merkle_tree([hashlib.sha256(reward.encode()).digest()])

    assert merkle_tree is not None
    return merkle_tree.tree_hash


@pytest.fixture
def merkle_root_with_2_transactions(reward, transfer) -> blocks.Hash:
    """ """
    merkle_tree = transacts.init_merkle_tree(
        [
            hashlib.sha256(reward.encode()).digest(),
            hashlib.sha256(transfer.encode()).digest(),
        ]
    )

    assert merkle_tree is not None
    return merkle_tree.tree_hash


@pytest.fixture
def blockchain_with_1_block() -> blocks.Blockchain:
    """ """
    block = blocks.init_genesis_block()
    block_hash = hashlib.sha256(hashlib.sha256(block.header.encode()).digest()).digest()

    return blocks.Blockchain(chain=[block_hash], blocks={block_hash: block})


@pytest.fixture
def blockchain_with_2_blocks(
    reward, transfer, merkle_root_with_2_transactions
) -> blocks.Blockchain:
    """ """
    block = blocks.init_genesis_block()
    block_hash = hashlib.sha256(hashlib.sha256(block.header.encode()).digest()).digest()

    blockchain = blocks.Blockchain(chain=[block_hash], blocks={block_hash: block})

    header = blocks.Header(
        version=blocks.VERSION,
        previous_hash=block_hash,
        merkle_root=merkle_root_with_2_transactions,
        timestamp=1634700600,
        nonce=14558,
    )

    block = blocks.Block(header=header, transactions=[reward, transfer])
    block_hash = hashlib.sha256(hashlib.sha256(header.encode()).digest()).digest()

    blockchain.chain.append(block_hash)
    blockchain.blocks[block_hash] = block

    return blockchain


def test_proof_of_work(merkle_root_with_1_transaction, merkle_root_with_2_transactions):
    """ """
    previous_hash = (0).to_bytes(32, byteorder="big")
    timestamp = 1634700000

    is_new_block, nonce, block_hash, header = blocks.run_proof_of_work(
        previous_hash, merkle_root_with_1_transaction, timestamp, 0, 1000
    )

    assert not is_new_block
    assert nonce == 1000
    assert block_hash is None
    assert header is None

    is_new_block, nonce, block_hash, header = blocks.run_proof_of_work(
        previous_hash, merkle_root_with_1_transaction, timestamp, 54000, 1000
    )

    assert is_new_block
    assert nonce == 54026
    assert (
        bytes.hex(block_hash)
        == "0000750f8d91e53b2f3ed764518c77c4bc50cd53c014bbe4bf5aaf89009b7d25"
    )
    assert (
        bytes.hex(header.encode())
        == "010000000000000000000000000000000000000000000000000000000000000000281d8712b36b4365bd09fe91de46e78b69d5d4ecf078252eb35b2cbbb24ba057616f8ae0000000000000000000000000000000000000000000000000000000000000d30a"
    )

    previous_hash = block_hash
    timestamp = 1634700600

    is_new_block, nonce, block_hash, header = blocks.run_proof_of_work(
        previous_hash, merkle_root_with_2_transactions, timestamp, 0, 1000
    )

    assert not is_new_block
    assert nonce == 1000
    assert block_hash is None
    assert header is None

    is_new_block, nonce, block_hash, header = blocks.run_proof_of_work(
        previous_hash, merkle_root_with_2_transactions, timestamp, 14000, 1000
    )

    assert is_new_block
    assert nonce == 14558
    assert (
        bytes.hex(block_hash)
        == "000075c4d199b464a8a9907f54bf6e20057978db79797867cbbe8d553854b8b4"
    )
    assert (
        bytes.hex(header.encode())
        == "010000750f8d91e53b2f3ed764518c77c4bc50cd53c014bbe4bf5aaf89009b7d25c1dcd5b493c8667c3ce50a62fb660cb545074f8d63bf2424bcff323005130179616f8d3800000000000000000000000000000000000000000000000000000000000038de"
    )


def test_validate_blockchain(
    reward,
    merkle_root_with_1_transaction,
    blockchain_with_1_block,
    blockchain_with_2_blocks,
):
    """ """
    blockchain = blockchain_with_1_block
    assert blocks.validate_blockchain(blockchain)

    blockchain = blockchain_with_2_blocks
    assert blocks.validate_blockchain(blockchain)

    # Intentionally use zero previous hash to obtain invalid blockchain.
    _, _, _, header = blocks.run_proof_of_work(
        (0).to_bytes(32, byteorder="big"),
        merkle_root_with_1_transaction,
        1634701200,
        174000,
        1000,
    )

    block = blocks.Block(header=header, transactions=[reward])
    block_hash = hashlib.sha256(hashlib.sha256(header.encode()).digest()).digest()

    blockchain.chain.append(block_hash)
    blockchain.blocks[block_hash] = block

    assert not blocks.validate_blockchain(blockchain)


def test_replace_blockchain(blockchain_with_1_block, blockchain_with_2_blocks):
    """ """
    assert blocks.replace_blockchain(blockchain_with_1_block, blockchain_with_2_blocks)
    assert not blocks.replace_blockchain(
        blockchain_with_1_block, blockchain_with_1_block
    )


def test_decode_message():
    """ """
    block = blocks.init_genesis_block()
    block_hash = hashlib.sha256(hashlib.sha256(block.header.encode()).digest()).digest()
    blockchain = blocks.Blockchain(chain=[block_hash], blocks={block_hash: block})
    blockchain_bytes = blockchain.encode()

    assert blocks.decode_blockchain(blockchain_bytes).encode() == blockchain_bytes
