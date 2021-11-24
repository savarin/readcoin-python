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
    return blocks.init_blockchain()


@pytest.fixture
def blockchain_with_2_blocks(
    reward, transfer, merkle_root_with_2_transactions
) -> blocks.Blockchain:
    """ """
    blockchain = blocks.init_blockchain()

    header = blocks.Header(
        version=blocks.VERSION,
        previous_hash=blockchain.chain[0],
        merkle_root=merkle_root_with_2_transactions,
        timestamp=1634700600,
        nonce=22025,
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
        previous_hash, merkle_root_with_1_transaction, timestamp, 102000, 1000
    )

    assert is_new_block
    assert nonce == 102275
    assert (
        bytes.hex(block_hash)
        == "0000e07d18285944711e785cfa7aa96443ddc9a4dfacce935d3bbc9793181ad6"
    )
    assert (
        bytes.hex(header.encode())
        == "000000000000000000000000000000000000000000000000000000000000000000281d8712b36b4365bd09fe91de46e78b69d5d4ecf078252eb35b2cbbb24ba057616f8ae00000000000000000000000000000000000000000000000000000000000018f83"
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
        previous_hash, merkle_root_with_2_transactions, timestamp, 22000, 1000
    )

    assert is_new_block
    assert nonce == 22025
    assert (
        bytes.hex(block_hash)
        == "00005b938d4fcaa18d0ccc4792100c5bcea26e0b56faec2334c8ea9d530c527e"
    )
    assert (
        bytes.hex(header.encode())
        == "000000e07d18285944711e785cfa7aa96443ddc9a4dfacce935d3bbc9793181ad6c1dcd5b493c8667c3ce50a62fb660cb545074f8d63bf2424bcff323005130179616f8d380000000000000000000000000000000000000000000000000000000000005609"
    )


def test_decode_message():
    """ """
    block = blocks.init_genesis_block()
    block_hash = hashlib.sha256(hashlib.sha256(block.header.encode()).digest()).digest()
    blockchain = blocks.Blockchain(chain=[block_hash], blocks={block_hash: block})
    blockchain_bytes = blockchain.encode()

    assert blocks.decode_blockchain(blockchain_bytes).encode() == blockchain_bytes
