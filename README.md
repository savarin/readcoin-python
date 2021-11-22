# readcoin

Minimal implementation of the Bitcoin protocol for educational purposes.

## Context

The latest version implements mining, blockchain validation (block hashes form a chain and satisfy
proof-of-work) and transaction validation (sender in receipt of token and has not been spent). For
simplicity, difficulty is set at a constant and each token is indivisible.

We implement the Bitcoin protocol through multiple iterations:

* [v1](https://github.com/savarin/readcoin/tree/v1) -
mining and blockchain validation only, each block as a bytestring.
* [v2](https://github.com/savarin/readcoin/tree/v2) -
include blockchain class implementation with encode/decode semantics.
* [v3](https://github.com/savarin/readcoin/tree/main) -
include Merkle tree and transaction validation (in progress).

The term readcoin refers to a blog by the author on readcoin.com (no longer operational). The first
article can be found [here](https://gist.github.com/savarin/c71c1e4dfa4edf3b13bf36ccd8f6de17).

Future plans include cryptographic signing of transactions.

## Installation

Running the code requires a single import.

```shell
pip install python-dotenv
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
