import os
import dataclasses
import socket

import dotenv

import helpers


dotenv.load_dotenv()

SENDER_IP = os.getenv("SENDER_IP")
RECEIVER_IP = os.getenv("RECEIVER_IP")


@dataclasses.dataclass
class Receiver:
    """ """

    sock: socket.socket


def init_receiver() -> Receiver:
    """ """
    assert RECEIVER_IP is not None
    sock = helpers.bind_socket(RECEIVER_IP, 7000)

    return Receiver(sock=sock)


def listen(receiver: Receiver):
    """ """
    while True:
        try:
            receiver.sock.settimeout(3)
            message, _ = receiver.sock.recvfrom(1024)
            print(message)
        except socket.timeout:
            print(".")


if __name__ == "__main__":
    receiver = init_receiver()
    listen(receiver)
