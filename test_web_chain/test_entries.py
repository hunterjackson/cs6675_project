from base64 import standard_b64decode

import pytest

from web_chain.entries import *

BYTES_32: bytes = (1234567890).to_bytes(length=32, byteorder='big')
BYTES_7: bytes = (1234567890).to_bytes(length=7, byteorder='big')


def test_root_entry():
    assert RootEntry._INSTANCE is None
    root_entry = RootEntry.get_instance()
    assert isinstance(root_entry, RootEntry)
    assert root_entry is RootEntry._INSTANCE
    assert RootEntry.get_instance() is root_entry
    assert root_entry.sha256_hash == (0).to_bytes(length=8, byteorder='big')
    assert root_entry.previous_entry == root_entry

    with pytest.raises(AttributeError):
        root_entry.sha256_hash = 456789

    with pytest.raises(AttributeError):
        root_entry.previous_entry = root_entry


def test_document_publish_entry():
    entry_1_expected_hash = standard_b64decode('eWlku996mzoL1UTIzAQyvdPtZlx5S8w+h3uNPrkakvk=')
    entry_1 = DocumentPublishEntry(previous_entry=RootEntry.get_instance(), public_key=BYTES_32, doc_id=BYTES_32)
    assert entry_1.previous_entry == RootEntry.get_instance()
    # print(standard_b64encode(entry_1.sha256_hash).decode('utf8'))
    assert entry_1.sha256_hash == entry_1_expected_hash
    assert entry_1.doc_id == BYTES_32
    assert entry_1.public_key == BYTES_32

    entry_2_expected_hash = standard_b64decode('NPa5KwXZhWzKfmI7vayWb35/RcP7mo/OKwoxJbkGHiw=')
    entry_2 = DocumentPublishEntry(previous_entry=entry_1, public_key=BYTES_32, doc_id=BYTES_32)
    assert entry_2.previous_entry == entry_1
    assert entry_2.sha256_hash != entry_1.sha256_hash
    # print(standard_b64encode(entry_2.sha256_hash).decode('utf8'))
    assert entry_2.sha256_hash == entry_2_expected_hash
    assert entry_2.doc_id == BYTES_32
    assert entry_2.public_key == BYTES_32

    with pytest.raises(AssertionError):
        DocumentPublishEntry(previous_entry=RootEntry.get_instance(), public_key=BYTES_7, doc_id=BYTES_32)
    with pytest.raises(AssertionError):
        DocumentPublishEntry(previous_entry=RootEntry.get_instance(), public_key=BYTES_32, doc_id=BYTES_7)


def test_document_update_entry():
    entry_1_expected_hash = standard_b64decode('jOz45FJTLr0DO2e4tPLhTvqKasPCI59knptUVcvXOqE=')
    entry_1 = DocumentUpdateEntry(previous_entry=RootEntry.get_instance(), public_key=BYTES_32, doc_id=BYTES_32,
                                  previous_doc_id=BYTES_32)
    assert entry_1.previous_entry == RootEntry.get_instance()
    # print(standard_b64encode(entry_1.sha256_hash).decode('utf8'))
    assert entry_1.sha256_hash == entry_1_expected_hash
    assert entry_1.doc_id == BYTES_32
    assert entry_1.public_key == BYTES_32
    assert entry_1.previous_doc_id == BYTES_32

    entry_2_expected_hash = standard_b64decode('r4gmNQpV/Q90f1vKUaQd73PQT4NoW158jv4HDl/pgRs=')
    entry_2 = DocumentUpdateEntry(previous_entry=entry_1, public_key=BYTES_32, doc_id=BYTES_32,
                                  previous_doc_id=BYTES_32)
    assert entry_2.previous_entry == entry_1
    assert entry_2.sha256_hash != entry_1.sha256_hash
    # print(standard_b64encode(entry_2.sha256_hash).decode('utf8'))
    assert entry_2.sha256_hash == entry_2_expected_hash
    assert entry_2.doc_id == BYTES_32
    assert entry_2.public_key == BYTES_32

    with pytest.raises(AssertionError):
        DocumentUpdateEntry(previous_entry=RootEntry.get_instance(), public_key=BYTES_32, doc_id=BYTES_32,
                            previous_doc_id=BYTES_7)


IP_ADDRESS = '127.0.0.1:8080'.encode('utf8')


def test_host_location_entry():
    entry_1_expected_hash = standard_b64decode('AXWHwNy2H5WjrO2jebfga43fn4ySuLxKkWe3pIjpozY=')
    entry_1 = HostLocationEntry(previous_entry=RootEntry.get_instance(), public_key=BYTES_32, ipaddress=IP_ADDRESS)
    assert entry_1.previous_entry == RootEntry.get_instance()
    # print(standard_b64encode(entry_1.sha256_hash).decode('utf8'))
    assert entry_1.sha256_hash == entry_1_expected_hash
    assert entry_1.public_key == BYTES_32
    assert entry_1.ipaddress == IP_ADDRESS

    entry_2_expected_hash = standard_b64decode('LA2Mc7VAEIbo7Bu4/wRlhWed44EjK8Ok+rDNrCsNZTY=')
    entry_2 = HostLocationEntry(previous_entry=entry_1, public_key=BYTES_32, ipaddress=IP_ADDRESS)
    assert entry_2.previous_entry == entry_1
    # print(standard_b64encode(entry_2.sha256_hash).decode('utf8'))
    assert entry_2.sha256_hash == entry_2_expected_hash
    assert entry_2.sha256_hash != entry_1.sha256_hash
    assert entry_2.public_key == BYTES_32
    assert entry_2.ipaddress == IP_ADDRESS
