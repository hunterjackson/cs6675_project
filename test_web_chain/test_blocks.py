from base64 import standard_b64decode

import pytest

from blocks import RootBlock, Block
from entries import RootEntry, DocumentPublishEntry, DocumentUpdateEntry

BYTES_32 = (1234567890).to_bytes(length=32, byteorder='big')


def test_root_block():
    block = RootBlock.get_instance()
    assert isinstance(block, RootBlock)
    assert block is RootBlock.get_instance()
    assert block.sha256_hash == (0).to_bytes(length=32, byteorder='big', signed=False)
    assert block.previous_block is block
    assert block.entries == (RootEntry.get_instance(),)
    assert block.nonce == 0
    with pytest.raises(Exception):
        RootBlock()


def test_block():
    entry_1 = DocumentPublishEntry(previous_entry=RootEntry.get_instance(), doc_id=BYTES_32, public_key=BYTES_32)
    entry_2 = DocumentUpdateEntry(previous_entry=entry_1, previous_doc_id=entry_1.doc_id, doc_id=BYTES_32,
                                  public_key=BYTES_32)
    block_1 = Block(previous_block=RootBlock.get_instance(), entries=[entry_1, entry_2])
    assert block_1.previous_block == RootBlock.get_instance()
    assert block_1.entries == (entry_1, entry_2)
    # print(standard_b64encode(block_1.sha256_hash).decode('utf8'))
    assert block_1.sha256_hash == standard_b64decode('BJhFt4a1og3gaSXoYorc1bGoIiBRSCznreJ7Ll4Dgxw=')
    print(block_1.nonce)
    block_2 = Block(previous_block=block_1, entries=[entry_1, entry_2])
    assert block_2.previous_block == block_1
    assert block_2.entries == (entry_1, entry_2)
    assert block_2.sha256_hash != block_1.sha256_hash
    # print(standard_b64encode(block_2.sha256_hash).decode('utf8'))
    assert block_2.sha256_hash == standard_b64decode('DGBTrzBtnTbqKNWMYsp5YnRl7R8EJo5dwC6zK6jQSgc=')
