import os
import json
import time
import asyncio
import hashlib
import logging
import argparse
from typing import Dict, Any, List

from aiohttp import web, ClientSession
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256


CHAIN_ID = "icoin-mainnet"
BLOCK_TIME = 5
BLOCK_REWARD = 25
MAX_MEMPOOL = 5000

DATA_DIR = "data"

CHAIN_FILE = f"{DATA_DIR}/chain.json"
STATE_FILE = f"{DATA_DIR}/state.json"
PEERS_FILE = f"{DATA_DIR}/peers.json"
VALIDATORS_FILE = f"{DATA_DIR}/validators.json"

os.makedirs(DATA_DIR, exist_ok=True)


# =============================================================================
# UTILS
# =============================================================================

def sha256(data: bytes):
    return hashlib.sha256(data).hexdigest()


def address_from_pub(pub):
    return sha256(pub.encode())[:40]


# =============================================================================
# STORAGE
# =============================================================================

def load_json(path, default):

    if not os.path.exists(path):
        return default

    with open(path) as f:
        return json.load(f)


def save_json(path, data):

    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# =============================================================================
# WALLET
# =============================================================================

def wallet_create():

    key = ECC.generate(curve="P-256")

    private_key = key.export_key(format="PEM")
    public_key = key.public_key().export_key(format="PEM")

    address = address_from_pub(public_key)

    return {
        "private_key": private_key,
        "public_key": public_key,
        "address": address
    }


def sign_tx(priv, tx):

    key = ECC.import_key(priv)

    payload = json.dumps(tx, sort_keys=True).encode()

    h = SHA256.new(payload)

    signer = DSS.new(key, "fips-186-3")

    sig = signer.sign(h).hex()

    return sig


def verify_sig(tx, sig, pub):

    try:

        key = ECC.import_key(pub)

        payload = json.dumps(tx, sort_keys=True).encode()

        h = SHA256.new(payload)

        verifier = DSS.new(key, "fips-186-3")

        verifier.verify(h, bytes.fromhex(sig))

        return True

    except Exception:
        return False


# =============================================================================
# BLOCK
# =============================================================================

class Block:

    def __init__(self, index, prev_hash, txs, validator, signature=None):

        self.index = index
        self.prev_hash = prev_hash
        self.txs = txs
        self.validator = validator
        self.timestamp = time.time()
        self.signature = signature

        self.hash = self.calc_hash()

    def calc_hash(self):

        payload = json.dumps({
            "index": self.index,
            "prev_hash": self.prev_hash,
            "txs": self.txs,
            "validator": self.validator,
            "timestamp": self.timestamp
        }, sort_keys=True).encode()

        return sha256(payload)

    def to_dict(self):

        return {
            "index": self.index,
            "prev_hash": self.prev_hash,
            "txs": self.txs,
            "validator": self.validator,
            "timestamp": self.timestamp,
            "hash": self.hash,
            "signature": self.signature
        }


# =============================================================================
# BLOCKCHAIN
# =============================================================================

class Blockchain:

    def __init__(self):

        self.chain: List[Block] = []

        self.mempool: List[Dict] = []

        self.state = load_json(STATE_FILE, {
            "balances": {},
            "nonce": {}
        })

        self.validators = load_json(VALIDATORS_FILE, [])

        if not self.validators:

            self.validators = ["genesis"]

            save_json(VALIDATORS_FILE, self.validators)

        self.load_chain()

    # -------------------------------------------------------------------------

    def load_chain(self):

        data = load_json(CHAIN_FILE, [])

        if not data:

            genesis = Block(0, "0", [], "genesis")

            self.chain.append(genesis)

            self.save_chain()

            return

        for b in data:

            block = Block(
                b["index"],
                b["prev_hash"],
                b["txs"],
                b["validator"],
                b.get("signature")
            )

            block.timestamp = b["timestamp"]
            block.hash = b["hash"]

            self.chain.append(block)

    # -------------------------------------------------------------------------

    def save_chain(self):

        save_json(CHAIN_FILE, [b.to_dict() for b in self.chain])

        save_json(STATE_FILE, self.state)

    # -------------------------------------------------------------------------

    def last_block(self):

        return self.chain[-1]

    # -------------------------------------------------------------------------

    def leader(self):

        height = len(self.chain)

        return self.validators[height % len(self.validators)]

    # -------------------------------------------------------------------------

    def validate_tx(self, tx_obj):

        tx = tx_obj["tx"]

        sig = tx_obj["signature"]

        pub = tx_obj["public_key"]

        if not verify_sig(tx, sig, pub):
            return False

        sender = tx["from"]

        if sender != "network":

            bal = self.state["balances"].get(sender, 0)

            if bal < tx["amount"]:
                return False

            nonce = self.state["nonce"].get(sender, 0)

            if tx["nonce"] != nonce:
                return False

        return True

    # -------------------------------------------------------------------------

    def add_tx(self, tx):

        if len(self.mempool) > MAX_MEMPOOL:
            return False

        if not self.validate_tx(tx):
            return False

        tx_hash = sha256(json.dumps(tx, sort_keys=True).encode())

        for m in self.mempool:
            if m["hash"] == tx_hash:
                return False

        tx["hash"] = tx_hash

        self.mempool.append(tx)

        return True

    # -------------------------------------------------------------------------

    def apply_tx(self, tx):

        sender = tx["from"]

        to = tx["to"]

        amount = tx["amount"]

        if sender != "network":

            self.state["balances"][sender] -= amount

            self.state["nonce"][sender] += 1

        self.state["balances"][to] = self.state["balances"].get(to, 0) + amount

    # -------------------------------------------------------------------------

    def create_block(self, validator):

        reward_tx = {
            "from": "network",
            "to": validator,
            "amount": BLOCK_REWARD,
            "nonce": 0
        }

        txs = [{"tx": reward_tx}] + self.mempool[:]

        self.mempool.clear()

        block = Block(
            len(self.chain),
            self.last_block().hash,
            txs,
            validator
        )

        for t in txs:
            self.apply_tx(t["tx"])

        self.chain.append(block)

        self.save_chain()

        return block


# =============================================================================
# NETWORK
# =============================================================================

class Network:

    def __init__(self):

        self.peers = load_json(PEERS_FILE, [])

    def add_peer(self, peer):

        if peer not in self.peers:

            self.peers.append(peer)

            save_json(PEERS_FILE, self.peers)

    async def gossip(self, endpoint, payload):

        async with ClientSession() as session:

            for peer in self.peers:

                try:
                    await session.post(peer + endpoint, json=payload)
                except:
                    pass

    async def sync_chain(self):

        async with ClientSession() as session:

            for peer in self.peers:

                try:

                    r = await session.get(peer + "/blocks")

                    remote = await r.json()

                    return remote

                except:
                    pass

        return None


# =============================================================================
# NODE
# =============================================================================

class Node:

    def __init__(self):

        self.blockchain = Blockchain()

        self.network = Network()

        self.node_id = os.getenv("NODE_ID", "node")

    async def forge(self):

        while True:

            await asyncio.sleep(BLOCK_TIME)

            leader = self.blockchain.leader()

            if leader != self.node_id:
                continue

            block = self.blockchain.create_block(self.node_id)

            logging.info("block forged %s", block.hash)

            await self.network.gossip("/block", block.to_dict())


node = Node()

routes = web.RouteTableDef()


# =============================================================================
# API
# =============================================================================

@routes.get("/wallet/create")
async def wallet_api(request):

    return web.json_response(wallet_create())


@routes.post("/tx")
async def tx_api(request):

    data = await request.json()

    ok = node.blockchain.add_tx(data)

    if ok:
        await node.network.gossip("/tx", data)

    return web.json_response({"ok": ok})


@routes.post("/block")
async def block_api(request):

    data = await request.json()

    if data["prev_hash"] != node.blockchain.last_block().hash:
        return web.json_response({"ok": False})

    block = Block(
        data["index"],
        data["prev_hash"],
        data["txs"],
        data["validator"],
        data.get("signature")
    )

    block.timestamp = data["timestamp"]

    block.hash = data["hash"]

    node.blockchain.chain.append(block)

    node.blockchain.save_chain()

    return web.json_response({"ok": True})


@routes.post("/peer")
async def peer_api(request):

    data = await request.json()

    node.network.add_peer(data["peer"])

    return web.json_response({"ok": True})


@routes.get("/blocks")
async def blocks_api(request):

    return web.json_response([b.to_dict() for b in node.blockchain.chain])


@routes.get("/mempool")
async def mempool_api(request):

    return web.json_response(node.blockchain.mempool)


@routes.get("/balance/{addr}")
async def balance_api(request):

    addr = request.match_info["addr"]

    return web.json_response({
        "balance": node.blockchain.state["balances"].get(addr, 0)
    })


# =============================================================================
# APP
# =============================================================================

async def startup(app):

    app["forge"] = asyncio.create_task(node.forge())


async def cleanup(app):

    app["forge"].cancel()


app = web.Application()

app.add_routes(routes)

app.on_startup.append(startup)

app.on_cleanup.append(cleanup)


# =============================================================================
# CLI
# =============================================================================

def cli():

    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("wallet")

    args = parser.parse_args()

    if args.cmd == "wallet":

        w = wallet_create()

        print(json.dumps(w, indent=2))


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    if len(os.sys.argv) > 1:

        cli()

    else:

        logging.basicConfig(level=logging.INFO)

        web.run_app(app, port=8080)
