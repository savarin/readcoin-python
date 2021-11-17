import binascii
import dataclasses
import os
import socket
import sys
import time

import dotenv

import blocks
import helpers


dotenv.load_dotenv()

NODE_IP = os.getenv("NODE_IP")
NODE_PORTS = [7000, 8000, 9000]


GENESIS_HASH, GENESIS_BLOCK = blocks.init_genesis_block()


@dataclasses.dataclass
class Node:
    """ """

    port: int
    sock: socket.socket
    blockchain: bytes
    block_counter: int


def init_node(port: int, blockchain: bytes = b"", block_counter: int = 0) -> Node:
    """ """
    assert NODE_IP is not None
    sock = helpers.bind_socket(NODE_IP, port)

    return Node(
        port=port, sock=sock, blockchain=blockchain, block_counter=block_counter
    )


def broadcast(node: Node, message: bytes):
    """ """
    for node_port in NODE_PORTS:
        if node_port == node.port:
            continue

        node.sock.sendto(message, (NODE_IP, node_port))


def run(node: Node):
    """ """
    previous_hash = GENESIS_HASH
    timestamp = int(time.time())
    nonce = 0

    while True:
        try:
            # Listen for incoming messages, with maximum size set at OS X maximum UDP package size
            # of 9216 bytes.
            node.sock.settimeout(1)
            blockchain, _ = node.sock.recvfrom(9216)

            # Check blockchain received is valid.
            is_new_block, block_counter, current_hash = blocks.validate_blockchain(
                blockchain
            )

            # Skip if invalid or not longer than existing blockchain.
            if not is_new_block or block_counter <= node.block_counter:
                print("IGNORE blockchain...")
                continue

            # Replace if valid and longer than existing.
            node.blockchain = blockchain
            node.block_counter = block_counter

            assert current_hash is not None
            print(
                f"COPY block {node.block_counter - 1}: {binascii.hexlify(current_hash).decode()}!"
            )

            # Force sleep to randomize timestamp.
            sleep_time = (node.port + block_counter) % 3 + 1
            print(f"SLEEP for {sleep_time} seconds...")
            time.sleep(sleep_time)

        except socket.timeout:
            # Run proof-of-work.
            print(f"TRY up to {nonce}...")
            is_new_block, _, current_hash, header = blocks.run_proof_of_work(
                previous_hash, timestamp, nonce, 1000
            )

            # Switch to listening mode if not solved after 1000 nonce values.
            if not is_new_block:
                nonce += 1000
                continue

            # Create transaction to award block if solved.
            assert current_hash is not None and header is not None
            transaction_counter, transactions = blocks.init_transactions(node.port)
            block = blocks.init_block(header, transaction_counter, transactions)

            node.blockchain += block
            node.block_counter += 1

            # Broadcast full blockchain to network.
            broadcast(node, node.blockchain)
            print(
                f"CREATE block {node.block_counter - 1}: {binascii.hexlify(current_hash).decode()}!"
            )

        # Reset values for next block header.
        previous_hash = current_hash
        timestamp = int(time.time())
        nonce = 0


if __name__ == "__main__":
    port = int(sys.argv[1])
    assert port in NODE_PORTS

    node = init_node(port, GENESIS_BLOCK, 1)
    run(node)
