from typing import DefaultDict, List, Optional, Tuple
import collections
import dataclasses
import hashlib

import blocks
import transactions as transacts


Accounts = DefaultDict[int, List[transacts.Hash]]


@dataclasses.dataclass
class Balance:
    """ """

    latest_hash: transacts.Hash
    accounts: Accounts


def update_accounts(accounts: Accounts, block: blocks.Block) -> Accounts:
    """ """
    for transaction in block.transactions:
        if transaction.sender != 0:
            accounts[transaction.sender].remove(transaction.reference_hash)

        reference_hash = hashlib.sha256(transaction.encode()).digest()
        accounts[transaction.receiver].append(reference_hash)

    return accounts


def init_balance(blockchain: blocks.Blockchain) -> Balance:
    """ """
    accounts: Accounts = collections.defaultdict(list)

    for block_hash in blockchain.chain:
        block = blockchain.blocks[block_hash]
        accounts = update_accounts(accounts, block)

    return Balance(latest_hash=block_hash, accounts=accounts)


def update_balance(balance: Balance, block: blocks.Block) -> Balance:
    """ """
    block_hash = hashlib.sha256(hashlib.sha256(block.header.encode()).digest()).digest()
    balance.latest_hash = block_hash

    balance.accounts = update_accounts(balance.accounts, block)

    return balance


def init_transfer(
    balance: Balance, sender: int, receiver: int
) -> Tuple[Optional[Balance], Optional[transacts.Transaction]]:
    """ """
    if sender not in balance.accounts or len(balance.accounts[sender]) == 0:
        return None, None

    reference_hash = balance.accounts[sender].pop(0)
    transaction = transacts.Transaction(
        reference_hash=reference_hash, sender=sender, receiver=receiver
    )

    return balance, transaction


def validate_transaction(balance: Balance, transaction: transacts.Transaction) -> bool:
    """ """
    sender = transaction.sender

    is_zero_reference = transaction.reference_hash == blocks.REWARD_HASH
    is_zero_sender = sender == 0

    if is_zero_reference and is_zero_sender:
        return True

    if is_zero_reference != is_zero_sender:
        return False

    if sender not in balance.accounts or len(balance.accounts[sender]) == 0:
        return False

    return transaction.reference_hash in balance.accounts[transaction.sender]


def validate_block(
    block: blocks.Block, previous_hash: transacts.Hash, balance: Balance
) -> Tuple[bool, Optional[transacts.Hash]]:
    """ """
    is_valid_header, current_hash = blocks.validate_header(block.header, previous_hash)

    if not is_valid_header:
        return False, None

    for transaction in block.transactions:
        is_valid_transaction = validate_transaction(balance, transaction)

        if not is_valid_transaction:
            return False, None

    return True, current_hash


def validate_blockchain(
    blockchain: blocks.Blockchain, balance: Optional[Balance] = None
) -> Tuple[bool, Optional[Balance]]:
    """Check that all headers in the blockchain satisfy proof-of-work and indeed form a chain."""
    if balance is None:
        balance = init_balance(blocks.init_blockchain())

    previous_hash = balance.latest_hash
    block_index = blockchain.chain.index(previous_hash)

    for block_hash in blockchain.chain[block_index + 1 :]:
        block = blockchain.blocks[block_hash]
        is_valid_block, current_hash = validate_block(block, previous_hash, balance)

        if not is_valid_block:
            return False, None

        assert current_hash is not None
        previous_hash = current_hash
        balance = update_balance(balance, block)

    return True, balance


def replace_blockchain(
    potential_blockchain: blocks.Blockchain,
    current_blockchain: blocks.Blockchain,
    balance: Optional[Balance] = None,
) -> Tuple[bool, Optional[Balance]]:
    """Compare blockchains and replace if potential blockchain is longer and valid."""
    current_chain = current_blockchain.chain

    if len(potential_blockchain.chain) <= len(current_chain):
        return False, None

    for i, block_hash in enumerate(potential_blockchain.chain):
        if i == len(current_chain) or block_hash != current_chain[i]:
            break

    if balance is not None:
        latest_index = current_chain.index(balance.latest_hash)

        if latest_index <= i:
            return validate_blockchain(potential_blockchain, balance)

    return validate_blockchain(potential_blockchain, None)
