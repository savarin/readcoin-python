from typing import List, Optional
import dataclasses
import hashlib


@dataclasses.dataclass
class MerkleTree:
    """ """

    tree_hash: bytes
    left: Optional["MerkleTree"] = None
    right: Optional["MerkleTree"] = None


def init_merkle_tree(transactions: List[bytes]) -> Optional[MerkleTree]:
    """ """
    transaction_counter = len(transactions)

    if transaction_counter == 0:
        return None

    elif transaction_counter == 1:
        return MerkleTree(tree_hash=transactions[0], left=None, right=None)

    bit_length = transaction_counter.bit_length()
    largest_power_of_two = 1 << (bit_length - 1)

    if largest_power_of_two == transaction_counter:
        divider_index = transaction_counter >> 1
    else:
        divider_index = largest_power_of_two

    left = init_merkle_tree(transactions[:divider_index])
    right = init_merkle_tree(transactions[divider_index:])

    left_hash = left.tree_hash if left is not None else b""
    right_hash = right.tree_hash if right is not None else b""

    tree_hash = hashlib.sha256(left_hash + right_hash).digest()
    return MerkleTree(tree_hash=tree_hash, left=left, right=right)
