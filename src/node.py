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

HQ_IP = os.getenv("HQ_IP")
HQ_PORT = 6000

NODE_IP = os.getenv("NODE_IP")
NODE_PORTS = [7000, 8000, 9000]


GENESIS_HASH, GENESIS_BLOCK = blocks.init_genesis_block()


@dataclasses.dataclass
class Node:
    """ """

    port: int
    sock: socket.socket
    blockchain: bytes
    blockchain_length: int


def init_node(port: int) -> Node:
    """ """
    assert NODE_IP is not None
    sock = helpers.bind_socket(NODE_IP, port)

    return Node(port=port, sock=sock, blockchain=GENESIS_BLOCK, blockchain_length=1)


def listen(node: Node):
    """ """
    previous_hash = GENESIS_HASH
    timestamp = int(time.time())
    nonce = 0

    while True:
        try:
            node.sock.settimeout(0.001)
            message, _ = node.sock.recvfrom(1024)
            print(message)

        except socket.timeout:
            print(f"nonce: {nonce}")

            is_new_block, current_hash, block_header = blocks.solve_block_header(
                previous_hash, timestamp, nonce, 1000
            )

            if not is_new_block:
                nonce += 1000
                continue

            assert block_header is not None and current_hash is not None
            transaction_counter, transactions = blocks.init_transactions(node.port)
            block = blocks.init_block(block_header, transaction_counter, transactions)

            print(
                f"block {node.blockchain_length}: {binascii.hexlify(current_hash).decode()}"
            )
            node.blockchain += block
            node.blockchain_length += 1

            for node_port in NODE_PORTS:
                if node_port == node.port:
                    continue

                node.sock.sendto(node.blockchain, (NODE_IP, node_port))

            previous_hash = current_hash
            timestamp = int(time.time())
            nonce = 0


if __name__ == "__main__":
    port = int(sys.argv[1])
    assert port in NODE_PORTS

    node = init_node(port)
    listen(node)
