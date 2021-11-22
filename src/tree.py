from typing import List, Optional, Tuple
import dataclasses
import hashlib


Hash = bytes


@dataclasses.dataclass
class Tree:
    """ """

    tree_hash: bytes
    left: Optional["Tree"]
    right: Optional["Tree"]


def init_merkle_tree(transaction_hashes: List[Hash]) -> Optional[Tree]:
    """ """
    transaction_counter = len(transaction_hashes)

    if transaction_counter == 0:
        return None

    elif transaction_counter == 1:
        return Tree(tree_hash=transaction_hashes[0], left=None, right=None)

    bit_length = transaction_counter.bit_length()
    largest_power_of_two = 1 << (bit_length - 1)

    if largest_power_of_two == transaction_counter:
        divider_index = transaction_counter >> 1
    else:
        divider_index = largest_power_of_two

    left = init_merkle_tree(transaction_hashes[:divider_index])
    right = init_merkle_tree(transaction_hashes[divider_index:])

    assert left is not None and right is not None
    left_hash = left.tree_hash if left is not None else b""
    right_hash = right.tree_hash if right is not None else b""

    assert left_hash is not None or right_hash is not None
    tree_hash = hashlib.sha256(left_hash + right_hash).digest()

    return Tree(tree_hash=tree_hash, left=left, right=right)


def find_merkle_path(merkle_tree: Tree, transaction_hash: Hash) -> Optional[List[Hash]]:
    """ """
    queue: List[Tuple[List[bytes], Tree]] = [([merkle_tree.tree_hash], merkle_tree)]

    while queue:
        path, current_tree = queue.pop(0)

        if current_tree.tree_hash == transaction_hash:
            if len(path) > 1:
                path += [transaction_hash]

            return path

        left_tree = current_tree.left
        right_tree = current_tree.right

        if left_tree is not None:
            left_path = []

            if right_tree is not None:
                left_path += [right_tree.tree_hash]

            # left_path += [left_tree.tree_hash]
            queue.append((path + left_path, left_tree))

        if right_tree is not None:
            right_path = []

            if left_tree is not None:
                right_path += [left_tree.tree_hash]

            # right_path += [right_tree.tree_hash]
            queue.append((path + right_path, right_tree))

    return None


def validate_merkle_path(path: Optional[List[bytes]]):
    """ """
    if path is None:
        return False

    if len(path) == 1:
        return True

    path.reverse()

    root_hash = path.pop()
    candidate_tree = Tree(tree_hash=path[0], left=None, right=None)

    subtrees_in = [(candidate_tree.tree_hash, candidate_tree)]
    subtrees_out = []

    for i, child_hash in enumerate(path[1:]):
        while subtrees_in:
            current_hash, current_tree = subtrees_in.pop()

            left_hash = hashlib.sha256(current_hash + child_hash).digest()
            right_hash = hashlib.sha256(child_hash + current_hash).digest()

            current_left = Tree(tree_hash=left_hash, left=None, right=None)
            current_right = Tree(tree_hash=right_hash, left=None, right=None)

            current_tree.left = current_left
            current_tree.right = current_right

            subtrees_out += [(current_left.tree_hash, current_left)]
            subtrees_out += [(current_right.tree_hash, current_right)]

        subtrees_in = subtrees_out.copy()
        subtrees_out = []

    candidate_hashes = []
    queue = [candidate_tree]

    while queue:
        current_tree = queue.pop(0)

        if current_tree.left is not None:
            queue.append(current_tree.left)

        if current_tree.right is not None:
            queue.append(current_tree.right)

        if current_tree.left is None and current_tree.right is None:
            candidate_hashes.append(current_tree.tree_hash)

    return root_hash in candidate_hashes
