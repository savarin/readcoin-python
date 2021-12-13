# readcoin

readcoin is a minimal proof-of-work cryptocurrency based on the Bitcoin protocol.

## Context

The latest version implements mining, header validation (block hashes form a chain and satisfy
proof-of-work) and transaction validation (sender has not been spent token and signature is valid).
For simplicity, difficulty is set at a constant and each token is indivisible.

We implement the Bitcoin protocol through multiple iterations:

* [v1](https://github.com/savarin/readcoin/tree/v1) -
starting point of mining and header validation only, each block as a bytestring.
* [v2](https://github.com/savarin/readcoin/tree/v2) -
include blockchain class implementation with encode/decode semantics.
* [v3](https://github.com/savarin/readcoin/tree/v3) -
include Merkle tree and transaction validation.
* [v4](https://github.com/savarin/readcoin/tree/v4) -
include balances and full block validation.
* [v5](https://github.com/savarin/readcoin/tree/main) -
include elliptic curve signature and verification.

The term readcoin refers to a blog by the author on readcoin.com (no longer operational). The first
article can be found [here](https://gist.github.com/savarin/c71c1e4dfa4edf3b13bf36ccd8f6de17). A
blog post series with step-by-step discussion of the implementation is currently in progress; posts
published so far are [here](https://ezzeriesa.notion.site/A-minimal-Bitcoin-implementation-Fall-2021-9559908f03ad4cb7a09ee60a457198e2).

## Installation

Running the code requires installation of two packages.

```shell
pip install python-dotenv cryptography
```

The environment variable `NODE_IP` needs to be set up as messages are sent via UDP.

```shell
echo 'NODE_IP='"$(ipconfig getifaddr en0)" > src/.env
```

Next respectively run each line in different terminal windows.
```shell
python src/node.py 7000
python src/node.py 8000
python src/node.py 9000
```
