import binascii

import blocks


def test_proof_of_work():
    """ """
    previous_hash = (0).to_bytes(32, byteorder="big")
    timestamp = 1634700000

    is_new_block, nonce, current_hash, block = blocks.run_proof_of_work(
        previous_hash, timestamp, 0, 1000
    )
    assert not is_new_block
    assert nonce == 1000
    assert current_hash is None
    assert block is None

    is_new_block, nonce, current_hash, block = blocks.run_proof_of_work(
        previous_hash, timestamp, 70000, 1000
    )
    assert is_new_block
    assert nonce == 70822
    assert (
        binascii.hexlify(current_hash)
        == b"00001ff58495c3dc2a1aaa69ebca4e9b3e05e63e5a319fb73bcdccbcdbba1e72"
    )
    assert (
        binascii.hexlify(block)
        == b"000000000000000000000000000000000000000000000000000000000000000000616f8ae000000000000000000000000000000000000000000000000000000000000114a6"
    )

    previous_hash = current_hash
    timestamp = 1634700600

    is_new_block, nonce, current_hash, block = blocks.run_proof_of_work(
        previous_hash, timestamp, 0, 1000
    )
    assert not is_new_block
    assert nonce == 1000
    assert current_hash is None
    assert block is None

    is_new_block, nonce, current_hash, block = blocks.run_proof_of_work(
        previous_hash, timestamp, 58000, 1000
    )
    assert is_new_block
    assert nonce == 58768
    assert (
        binascii.hexlify(current_hash)
        == b"000071e6ff5b358e57339b42d45b20acc0f112c218fa435b3ffa8f239b777347"
    )
    assert (
        binascii.hexlify(block)
        == b"0000001ff58495c3dc2a1aaa69ebca4e9b3e05e63e5a319fb73bcdccbcdbba1e72616f8d38000000000000000000000000000000000000000000000000000000000000e590"
    )
