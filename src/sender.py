import os
import dataclasses
import socket

import dotenv

import helpers


dotenv.load_dotenv()

SENDER_IP = os.getenv("SENDER_IP")
RECEIVER_IP = os.getenv("RECEIVER_IP")


@dataclasses.dataclass
class Sender:
    """ """

    sock: socket.socket


def init_sender() -> Sender:
    """ """
    assert SENDER_IP is not None
    sock = helpers.bind_socket(SENDER_IP, 6000)

    return Sender(sock=sock)


def listen(sender: Sender):
    """ """
    while True:
        message = bytes.fromhex(input("> "))
        print(message)

        assert RECEIVER_IP is not None
        sender.sock.sendto(message, (RECEIVER_IP, 7000))


if __name__ == "__main__":
    sender = init_sender()
    listen(sender)
