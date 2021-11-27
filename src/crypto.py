from typing import Dict, Tuple, Union
import dataclasses
import hashlib

import cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

import transactions as transacts


SIGNATURE_ALGORITHM = ec.ECDSA(algorithm=cryptography.hazmat.primitives.hashes.SHA256())
ENCODING = serialization.Encoding.PEM
PUBLIC_FORMAT = serialization.PublicFormat.SubjectPublicKeyInfo
PRIVATE_FORMAT = serialization.PrivateFormat.PKCS8


def sign(private_key: ec.EllipticCurvePrivateKey, message: bytes) -> bytes:
    """ """
    return private_key.sign(message, SIGNATURE_ALGORITHM)


def verify(
    signature: bytes, public_key: ec.EllipticCurvePublicKey, message: bytes
) -> bool:
    """ """
    try:
        public_key.verify(signature, message, SIGNATURE_ALGORITHM)

    except cryptography.exceptions.InvalidSignature:
        return False

    return True


def save_keys(
    public_key: ec.EllipticCurvePublicKey,
    private_key: ec.EllipticCurvePrivateKey,
    name_prefix: str = "",
    require_password: bool = True,
):
    """ """
    password = None
    encryption_algorithm: Union[
        serialization.NoEncryption, serialization.BestAvailableEncryption
    ] = serialization.NoEncryption()

    if require_password:
        password = input("password: ").encode()
        encryption_algorithm = serialization.BestAvailableEncryption(password=password)

    serialized_public = public_key.public_bytes(encoding=ENCODING, format=PUBLIC_FORMAT)
    serialized_private = private_key.private_bytes(
        encoding=ENCODING,
        format=PRIVATE_FORMAT,
        encryption_algorithm=encryption_algorithm,
    )

    with open(f"../vectors/{name_prefix}public.pem", "wb") as f:
        f.write(serialized_public)

    with open(f"../vectors/{name_prefix}private.pem", "wb") as f:
        f.write(serialized_private)


def load_keys(
    name_prefix: str = "", require_password: bool = True
) -> Tuple[ec.EllipticCurvePublicKey, ec.EllipticCurvePrivateKey]:
    """ """
    password = None

    if require_password:
        password = input("password: ").encode()

    with open(f"../vectors/{name_prefix}public.pem", "rb") as f:
        serialized_public = f.read()

    with open(f"../vectors/{name_prefix}private.pem", "rb") as f:
        serialized_private = f.read()

    public_key = serialization.load_pem_public_key(serialized_public)
    private_key = serialization.load_pem_private_key(
        serialized_private, password=password
    )

    assert isinstance(public_key, ec.EllipticCurvePublicKey)
    assert isinstance(private_key, ec.EllipticCurvePrivateKey)

    return public_key, private_key


@dataclasses.dataclass
class Wallet:
    """ """

    address: bytes
    port: int
    public_key: ec.EllipticCurvePublicKey
    private_key: ec.EllipticCurvePrivateKey


def get_address(public_key: ec.EllipticCurvePublicKey) -> bytes:
    """ """
    return hashlib.sha256(
        public_key.public_bytes(
            encoding=ENCODING,
            format=PUBLIC_FORMAT,
        )
    ).digest()


def init_wallet(port: int) -> Wallet:
    """ """
    private_key = ec.generate_private_key(curve=ec.SECP256K1())
    public_key = private_key.public_key()
    address = get_address(public_key)

    return Wallet(
        address=address, port=port, public_key=public_key, private_key=private_key
    )


def sign_transfer(
    wallet: Wallet, reference_hash: transacts.Hash, receiver: transacts.Hash
) -> bytes:
    """ """
    return sign(wallet.private_key, reference_hash + receiver)


def init_demo_wallets(persist_keys: bool = False) -> Dict[int, Wallet]:
    """ """
    wallets: Dict[int, Wallet] = {}

    for port in [7000, 8000, 9000]:
        wallet = init_wallet(port=port)
        wallets[port] = wallet

        if persist_keys:
            name_prefix = str(port) + "-"
            save_keys(wallet.public_key, wallet.private_key, name_prefix, False)

    return wallets


def load_demo_wallets() -> Dict[int, Wallet]:
    """ """
    wallets: Dict[int, Wallet] = {}

    for port in [7000, 8000, 9000]:
        name_prefix = str(port) + "-"
        public_key, private_key = load_keys(name_prefix, False)

        address = get_address(public_key)
        wallet = Wallet(
            address=address, port=port, public_key=public_key, private_key=private_key
        )

        wallets[port] = wallet

    return wallets
