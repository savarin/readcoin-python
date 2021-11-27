import dataclasses
import hashlib
import os
import socket
import sys
import time

import dotenv

import balances
import blocks
import crypto
import transactions as transacts


dotenv.load_dotenv()

NODE_IP = os.getenv("NODE_IP")
NODE_PORTS = [7000, 8000, 9000]


def bind_socket(ip_address: str, port: int) -> socket.socket:
    """ """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip_address, port))
    return sock


@dataclasses.dataclass
class Node:
    """ """

    address: transacts.Hash
    port: int
    sock: socket.socket
    blockchain: blocks.Blockchain
    balance: balances.Balance


def init_node(port: int) -> Node:
    """ """
    assert NODE_IP is not None
    sock = bind_socket(NODE_IP, port)

    wallets = crypto.load_demo_wallets()
    address = wallets[port].address
    keychain = {wallet.address: wallet.public_key for _, wallet in wallets.items()}

    blockchain = blocks.init_blockchain(wallets[7000].address)
    balance = balances.init_balance(blockchain, keychain)

    return Node(
        address=address, port=port, sock=sock, blockchain=blockchain, balance=balance
    )


def broadcast(node: Node, message: bytes):
    """ """
    for node_port in NODE_PORTS:
        if node_port == node.port:
            continue

        node.sock.sendto(message, (NODE_IP, node_port))


def run(node: Node):
    """ """
    previous_hash = node.blockchain.chain[0]
    timestamp = int(time.time())
    nonce = 0

    while True:
        try:
            # Listen for incoming messages, with maximum size set at OS X maximum UDP package size
            # of 9216 bytes.
            node.sock.settimeout(0.1)
            message, _ = node.sock.recvfrom(9216)

            # Decode message and check blockchain is valid.
            blockchain = blocks.decode_blockchain(message)

            is_valid_blockchain, balance = balances.replace_blockchain(
                blockchain, node.blockchain, node.balance
            )

            if not is_valid_blockchain:
                print("IGNORE blockchain...")
                continue

            # Replace if valid and longer than existing.
            node.blockchain = blockchain
            blockchain_counter = len(blockchain.chain)
            block_hash = blockchain.chain[-1]

            print(f"COPY block {blockchain_counter - 1}: {bytes.hex(block_hash)}!")

            # Replace balance
            assert balance is not None
            node.balance = balance

            # Force sleep to randomize timestamp.
            sleep_time = (node.port + blockchain_counter) % 3 + 1
            print(f"SLEEP for {sleep_time} seconds...")
            time.sleep(sleep_time)

        except socket.timeout:
            reward = transacts.Transaction(
                reference_hash=transacts.REWARD_HASH,
                sender=transacts.REWARD_SENDER,
                receiver=node.address,
                signature=transacts.REWARD_SIGNATURE,
            )
            merkle_root = hashlib.sha256(reward.encode()).digest()

            # Run proof-of-work.
            print(f"TRY up to {nonce}...")
            is_new_block, _, current_hash, header = blocks.run_proof_of_work(
                previous_hash, merkle_root, timestamp, nonce, 1000
            )

            # Switch to listening mode if not solved after 1000 nonce values.
            if not is_new_block:
                nonce += 1000
                continue

            assert current_hash is not None
            block_hash = current_hash

            # Create block reward if solved.
            assert header is not None

            block = blocks.Block(header=header, transactions=[reward])

            # Append new block to blockchain.
            node.blockchain.chain.append(block_hash)
            node.blockchain.blocks[block_hash] = block

            # Broadcast full blockchain to network.
            broadcast(node, node.blockchain.encode())
            print(
                f"CREATE block {len(node.blockchain.chain) - 1}: {bytes.hex(block_hash)}!"
            )

            # Update balance
            node.balance = balances.update_balance(node.balance, block)

        # Reset values for next block header.
        previous_hash = block_hash
        timestamp = int(time.time())
        nonce = 0


if __name__ == "__main__":
    port = int(sys.argv[1])
    assert port in NODE_PORTS

    node = init_node(port)
    run(node)
