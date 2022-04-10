from base64 import standard_b64decode

import pytest

from blocks import RootBlock, Block
from entries import RootEntry, DocumentPublishEntry, DocumentUpdateEntry

BYTES_8 = (1234567890).to_bytes(length=8, byteorder='big')


def test_root_block():
    block = RootBlock.get_instance()
    assert isinstance(block, RootBlock)
    assert block is RootBlock.get_instance()
    assert block.sha256_hash == (0).to_bytes(length=8, byteorder='big', signed=False)
    assert block.previous_block is block
    assert block.entries == (RootEntry.get_instance(),)
    with pytest.raises(Exception):
        RootBlock()


def test_block():
    entry_1 = DocumentPublishEntry(previous_entry=RootEntry.get_instance(), doc_id=BYTES_8, public_key=BYTES_8)
    entry_2 = DocumentUpdateEntry(previous_entry=entry_1, previous_doc_id=entry_1.doc_id, doc_id=BYTES_8,
                                  public_key=BYTES_8)
    block_1 = Block(previous_block=RootBlock.get_instance(), entries=[entry_1, entry_2])
    assert block_1.previous_block == RootBlock.get_instance()
    assert block_1.entries == (entry_1, entry_2)
    assert block_1.sha256_hash == standard_b64decode('X1eiq3xdtKs5R+vYVtama92YbpKwFuJl1cracc7aGxc=')

    block_2 = Block(previous_block=block_1, entries=[entry_1, entry_2])
    assert block_2.previous_block == block_1
    assert block_2.entries == (entry_1, entry_2)
    assert block_2.sha256_hash != block_1.sha256_hash
    # print(standard_b64encode(block_2.sha256_hash).decode('utf8'))
    assert block_2.sha256_hash == standard_b64decode('7mm0hD8P5UhhmsM9HqRuddMCaa8jcL8bkANOTVfm1t4=')
