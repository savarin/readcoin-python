from typing import List, Optional, Tuple
import dataclasses
import hashlib


@dataclasses.dataclass
class MerkleTree:
    """ """

    tree_hash: bytes
    left: Optional["MerkleTree"] = None
    right: Optional["MerkleTree"] = None


def init_merkle_tree(transaction_hashes: List[bytes]) -> Optional[MerkleTree]:
    """ """
    transaction_counter = len(transaction_hashes)

    if transaction_counter == 0:
        return None

    elif transaction_counter == 1:
        return MerkleTree(tree_hash=transaction_hashes[0], left=None, right=None)

    bit_length = transaction_counter.bit_length()
    largest_power_of_two = 1 << (bit_length - 1)

    if largest_power_of_two == transaction_counter:
        divider_index = transaction_counter >> 1
    else:
        divider_index = largest_power_of_two

    left = init_merkle_tree(transaction_hashes[:divider_index])
    right = init_merkle_tree(transaction_hashes[divider_index:])

    left_hash = left.tree_hash if left is not None else b""
    right_hash = right.tree_hash if right is not None else b""

    tree_hash = hashlib.sha256(left_hash + right_hash).digest()
    return MerkleTree(tree_hash=tree_hash, left=left, right=right)


def find_merkle_path(
    merkle_tree: MerkleTree, transaction_hash: bytes
) -> Optional[List[bytes]]:
    """ """
    queue: List[Tuple[List[bytes], MerkleTree]] = [([], merkle_tree)]

    while queue:
        path, current_tree = queue.pop(0)
        current_hash = current_tree.tree_hash

        if current_tree.tree_hash == transaction_hash:
            path += [current_hash]
            return path

        if current_tree.left is not None:
            left_path = path + [current_hash]
            queue.append((left_path, current_tree.left))

        if current_tree.right is not None:
            right_path = path + [current_hash]
            queue.append((right_path, current_tree.right))

    return None
