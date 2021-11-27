from typing import Dict
import hashlib

import pytest

import balances
import blocks
import crypto
import transactions as transacts


@pytest.fixture
def wallets() -> Dict[int, crypto.Wallet]:
    """ """
    return crypto.load_demo_wallets()


@pytest.fixture
def keychain(wallets) -> balances.Keychain:
    """ """
    return {wallet.address: wallet.public_key for _, wallet in wallets.items()}


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


@pytest.fixture
def blockchain_with_2_blocks(
    wallets, reward, transfer, merkle_root_with_2_transactions
) -> blocks.Blockchain:
    """ """
    blockchain = blocks.init_blockchain(wallets[7000].address)

    header = blocks.Header(
        version=blocks.VERSION,
        previous_hash=blockchain.chain[0],
        merkle_root=merkle_root_with_2_transactions,
        timestamp=1634700600,
        nonce=38997,
    )

    block = blocks.Block(header=header, transactions=[reward, transfer])
    block_hash = hashlib.sha256(hashlib.sha256(header.encode()).digest()).digest()

    blockchain.chain.append(block_hash)
    blockchain.blocks[block_hash] = block

    return blockchain


def test_init_balance(
    wallets, keychain, blockchain_with_1_block, blockchain_with_2_blocks
):
    """ """
    balance = balances.init_balance(blockchain_with_1_block, keychain)

    assert (
        bytes.hex(balance.latest_hash)
        == "0000a0939d2ea8133efef4576aceac9e89b66298ecafce0615d1de4dc06db7c8"
    )
    assert len(balance.accounts) == 1

    assert len(balance.accounts[wallets[7000].address]) == 1
    assert (
        bytes.hex(balance.accounts[wallets[7000].address][0])
        == "78ab8e2fe28bb3faf504ef7684e73d999359284f80213a0de57d0dd4bba36783"
    )

    block_hash = blockchain_with_2_blocks.chain.pop()
    block = blockchain_with_2_blocks.blocks[block_hash]
    balance = balances.update_balance(balance, block)

    assert (
        bytes.hex(balance.latest_hash)
        == "000069db062f12a370e3614549bfc80f759e000b743b94387fd8d7740873a65e"
    )
    assert len(balance.accounts) == 2

    assert len(balance.accounts[wallets[7000].address]) == 1
    assert (
        bytes.hex(balance.accounts[wallets[7000].address][0])
        == "78ab8e2fe28bb3faf504ef7684e73d999359284f80213a0de57d0dd4bba36783"
    )

    assert len(balance.accounts[wallets[8000].address]) == 1
    assert (
        bytes.hex(balance.accounts[wallets[8000].address][0])
        == "4f80df918605f2c2a865e440080000833c77740d4e94629712e089136c5bee40"
    )


def test_init_transfer(wallets, keychain, blockchain_with_2_blocks):
    """ """
    balance = balances.init_balance(blockchain_with_2_blocks, keychain)
    reference_hash = balance.accounts[wallets[7000].address][0]

    _, transfer = balances.init_transfer(
        balance, wallets[7000].address, wallets[8000].address, b""
    )

    assert transfer == transacts.Transaction(
        reference_hash=reference_hash,
        sender=wallets[7000].address,
        receiver=wallets[8000].address,
        signature=b"",
    )


def test_validate_transaction(
    wallets, keychain, reward, transfer, blockchain_with_2_blocks
):
    """ """
    pre_transfer_balance = balances.init_balance(blockchain_with_2_blocks, keychain)

    assert balances.validate_transaction(pre_transfer_balance, reward)
    assert balances.validate_transaction(pre_transfer_balance, transfer)

    post_transfer_balance, _ = balances.init_transfer(
        pre_transfer_balance, wallets[7000].address, wallets[8000].address, b""
    )
    assert not balances.validate_transaction(post_transfer_balance, transfer)

    # Include check on non-immutability for closer review.
    assert id(pre_transfer_balance) == id(post_transfer_balance)


def test_validate_blockchain(
    keychain,
    reward,
    merkle_root_with_1_transaction,
    blockchain_with_1_block,
    blockchain_with_2_blocks,
):
    """ """
    balance = balances.init_balance(blockchain_with_1_block, keychain)

    is_valid_blockchain, _ = balances.validate_blockchain(
        blockchain_with_1_block, balance
    )
    assert is_valid_blockchain

    is_valid_blockchain, _ = balances.validate_blockchain(
        blockchain_with_2_blocks, balance
    )
    assert is_valid_blockchain

    # Intentionally use zero previous hash to obtain invalid blockchain.
    is_new_block, nonce, block_hash, header = blocks.run_proof_of_work(
        (0).to_bytes(32, byteorder="big"),
        merkle_root_with_1_transaction,
        1634701200,
        4800,
        1000,
    )

    block = blocks.Block(header=header, transactions=[reward])
    block_hash = hashlib.sha256(hashlib.sha256(header.encode()).digest()).digest()

    blockchain = blockchain_with_2_blocks

    blockchain.chain.append(block_hash)
    blockchain.blocks[block_hash] = block

    is_valid_blockchain, _ = balances.validate_blockchain(blockchain, balance)
    assert not is_valid_blockchain


def test_replace_blockchain(
    keychain, blockchain_with_1_block, blockchain_with_2_blocks
):
    """ """
    is_valid_blockchain, _ = balances.replace_blockchain(
        blockchain_with_2_blocks, blockchain_with_1_block, None, keychain
    )
    assert is_valid_blockchain

    is_valid_blockchain, _ = balances.replace_blockchain(
        blockchain_with_1_block, blockchain_with_1_block, None, keychain
    )
    assert not is_valid_blockchain
