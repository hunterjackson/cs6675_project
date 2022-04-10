from base64 import standard_b64decode

import pytest

from web_chain.entries import *

BYTES_8: bytes = (1234567890).to_bytes(length=8, byteorder='big')
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
    entry_1_expected_hash = standard_b64decode('V1u7mH7jgH+NJOEI/49957vLQIkwRIBq4QUuWosoH5I=')
    entry_1 = DocumentPublishEntry(previous_entry=RootEntry.get_instance(), public_key=BYTES_8, doc_id=BYTES_8)
    assert entry_1.previous_entry == RootEntry.get_instance()
    assert entry_1.sha256_hash == entry_1_expected_hash
    assert entry_1.doc_id == BYTES_8
    assert entry_1.public_key == BYTES_8

    entry_2_expected_hash = standard_b64decode('VpKO5sal9/hSJvP7cPOYhMjyZXk1gUiOrYCv5pJk3rM=')
    entry_2 = DocumentPublishEntry(previous_entry=entry_1, public_key=BYTES_8, doc_id=BYTES_8)
    assert entry_2.previous_entry == entry_1
    assert entry_2.sha256_hash != entry_1.sha256_hash
    assert entry_2.sha256_hash == entry_2_expected_hash
    assert entry_2.doc_id == BYTES_8
    assert entry_2.public_key == BYTES_8

    with pytest.raises(AssertionError):
        DocumentPublishEntry(previous_entry=RootEntry.get_instance(), public_key=BYTES_7, doc_id=BYTES_8)
    with pytest.raises(AssertionError):
        DocumentPublishEntry(previous_entry=RootEntry.get_instance(), public_key=BYTES_8, doc_id=BYTES_7)


def test_document_update_entry():
    entry_1_expected_hash = standard_b64decode('cghvs8K/p8BuU3E2SaqMA/VYCjvm1palmXKsVuBVSkg=')
    entry_1 = DocumentUpdateEntry(previous_entry=RootEntry.get_instance(), public_key=BYTES_8, doc_id=BYTES_8,
                                  previous_doc_id=BYTES_8)
    assert entry_1.previous_entry == RootEntry.get_instance()
    assert entry_1.sha256_hash == entry_1_expected_hash
    assert entry_1.doc_id == BYTES_8
    assert entry_1.public_key == BYTES_8
    assert entry_1.previous_doc_id == BYTES_8

    entry_2_expected_hash = standard_b64decode('bLdDMz9Wju1aoK2OWNxpYe9unXj7pccw5jo5S8g3S8o=')
    entry_2 = DocumentUpdateEntry(previous_entry=entry_1, public_key=BYTES_8, doc_id=BYTES_8, previous_doc_id=BYTES_8)
    assert entry_2.previous_entry == entry_1
    assert entry_2.sha256_hash != entry_1.sha256_hash
    assert entry_2.sha256_hash == entry_2_expected_hash
    assert entry_2.doc_id == BYTES_8
    assert entry_2.public_key == BYTES_8

    with pytest.raises(AssertionError):
        DocumentUpdateEntry(previous_entry=RootEntry.get_instance(), public_key=BYTES_8, doc_id=BYTES_8,
                            previous_doc_id=BYTES_7)


IP_ADDRESS = '127.0.0.1:8080'.encode('utf8')


def test_host_location_entry():
    entry_1_expected_hash = standard_b64decode('m1+Q9TJ1eR5Y34e7sLnFFkHTSZ3dsZeW5l2v0yrZmyQ=')
    entry_1 = HostLocationEntry(previous_entry=RootEntry.get_instance(), public_key=BYTES_8, ipaddress=IP_ADDRESS)
    assert entry_1.previous_entry == RootEntry.get_instance()
    assert entry_1.sha256_hash == entry_1_expected_hash
    assert entry_1.public_key == BYTES_8
    assert entry_1.ipaddress == IP_ADDRESS

    entry_2_expected_hash = standard_b64decode('fpYohNAfri6G1y1rB+vAJLRIFn1htzONLWumjIXBnOY=')
    entry_2 = HostLocationEntry(previous_entry=entry_1, public_key=BYTES_8, ipaddress=IP_ADDRESS)
    assert entry_2.previous_entry == entry_1
    assert entry_2.sha256_hash == entry_2_expected_hash
    assert entry_2.sha256_hash != entry_1.sha256_hash
    assert entry_2.public_key == BYTES_8
    assert entry_2.ipaddress == IP_ADDRESS
