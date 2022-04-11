from random import randint, randbytes
from typing import Tuple

from blocks import Block, RootBlock
from entries import DocumentPublishEntry, RootEntry


def gen_block() -> Tuple[Tuple[Block], dict]:
    num_entries = randint(2, 10)
    entries = [
        DocumentPublishEntry(previous_entry=RootEntry.get_instance(), doc_id=randbytes(32), public_key=randbytes(32))]
    for _ in range(num_entries):
        entries.append(DocumentPublishEntry(previous_entry=entries[-1], doc_id=randbytes(32), public_key=randbytes(32)))
    return (Block(previous_block=RootBlock.get_instance(), entries=entries),), {}


def test_nonce_calculation(benchmark):
    benchmark.pedantic(target=lambda x: x.sha256_hash, setup=gen_block, rounds=10_000)
