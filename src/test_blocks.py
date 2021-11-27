from typing import Dict
import hashlib

import pytest

import blocks
import crypto
import transactions as transacts


@pytest.fixture
def wallets() -> Dict[int, crypto.Wallet]:
    """ """
    return crypto.load_demo_wallets()


@pytest.fixture
def reward(wallets) -> transacts.Transaction:
    """ """
    return transacts.init_reward(wallets[7000].address)


@pytest.fixture
def transfer(wallets, reward) -> transacts.Transaction:
    """ """
    reference_hash = hashlib.sha256(reward.encode()).digest()
    sender = wallets[7000].address
    receiver = wallets[8000].address
    signature = bytes.fromhex(
        "3046022100908f0452a1cec2be556d2c06f38ea6e9c4f00c027eaabb561035e938f8d0bbce0221009b310b8274e29e6032c98ddc960b8406b2a282b1087a6219223af5488b2c0529"
    )

    return transacts.Transaction(
        reference_hash=reference_hash,
        sender=sender,
        receiver=receiver,
        signature=signature,
    )


@pytest.fixture
def merkle_root_with_1_transaction(reward) -> transacts.Hash:
    """ """
    merkle_tree = transacts.init_merkle_tree([hashlib.sha256(reward.encode()).digest()])

    assert merkle_tree is not None
    return merkle_tree.tree_hash


@pytest.fixture
def merkle_root_with_2_transactions(reward, transfer) -> transacts.Hash:
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
def blockchain_with_1_block(wallets) -> blocks.Blockchain:
    """ """
    return blocks.init_blockchain(wallets[7000].address)


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
        previous_hash, merkle_root_with_1_transaction, timestamp, 82000, 1000
    )

    assert is_new_block
    assert nonce == 82822
    assert (
        bytes.hex(block_hash)
        == "0000a0939d2ea8133efef4576aceac9e89b66298ecafce0615d1de4dc06db7c8"
    )
    assert (
        bytes.hex(header.encode())
        == "00000000000000000000000000000000000000000000000000000000000000000078ab8e2fe28bb3faf504ef7684e73d999359284f80213a0de57d0dd4bba36783616f8ae00000000000000000000000000000000000000000000000000000000000014386"
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
        previous_hash, merkle_root_with_2_transactions, timestamp, 38000, 1000
    )

    assert is_new_block
    assert nonce == 38997
    assert (
        bytes.hex(block_hash)
        == "000069db062f12a370e3614549bfc80f759e000b743b94387fd8d7740873a65e"
    )
    assert (
        bytes.hex(header.encode())
        == "000000a0939d2ea8133efef4576aceac9e89b66298ecafce0615d1de4dc06db7c8f76df9abcee1754029c9c4baae15bde25ce80eaf52427a3ed49c1641100c64de616f8d380000000000000000000000000000000000000000000000000000000000009855"
    )


def test_decode_blockchain(blockchain_with_1_block):
    """ """
    blockchain_bytes = blockchain_with_1_block.encode()

    assert blocks.decode_blockchain(blockchain_bytes).encode() == blockchain_bytes
