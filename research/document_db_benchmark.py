#!/usr/bin/env python3
import sqlite3
from base64 import b64encode
from collections import deque
from os.path import getsize
from random import randint, choice, shuffle
from time import perf_counter
from pathlib import Path
from sqlite3 import Connection
from tempfile import TemporaryDirectory
from timeit import Timer
from typing import List, Deque

DDL = '''
PRAGMA foreign_keys = ON;
CREATE TABLE location (
    public_key_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    public_key TEXT UNIQUE, 
    ip_address TEXT
);
CREATE TABLE document (
    doc_id TEXT PRIMARY KEY NOT NULL, 
    previous_doc_id TEXT UNIQUE, 
    public_key_id INTEGER NOT NULL, 
    FOREIGN KEY(public_key_id) REFERENCES location(public_key_id)
);
'''

QUERY = '''
SELECT 
    location.public_key,
    location.ip_address,
    document.previous_doc_id
FROM document
LEFT JOIN location ON document.public_key_id = location.public_key_id
WHERE document.doc_id = ?
'''

NUM_HOSTS = 100
NUM_DOCUMENTS_PER_HOST = 1_000
NUM_TEST_QUERIES = 10_000


def create_database(db_dir: Path) -> Connection:
    location = db_dir / 'document_db_benchmark.sqlite3'
    conn = sqlite3.connect(location)
    conn.executescript(DDL)
    return location, conn


def random_public_key() -> str:
    return b64encode(randint(0, 2 ** (8 * 512)).to_bytes(512, 'little')).decode('ascii')


def random_doc_id() -> str:
    return b64encode(randint(0, 2 ** (8 * 256)).to_bytes(256, 'little')).decode('ascii')


def random_ip_address() -> str:
    return '.'.join(str(randint(0, 256)) for _ in range(4))


def fill_database(conn: Connection) -> List[str]:
    next_pk_id = conn.execute('select max(public_key_id) from location').fetchall()[0][0]
    next_pk_id = 0 if next_pk_id is None else next_pk_id + 1
    location_data = [(ix, random_public_key(), random_ip_address()) for ix in range(next_pk_id, NUM_HOSTS + next_pk_id)]

    start_time = perf_counter()
    conn.executemany('INSERT INTO location (public_key_id, public_key, ip_address) VALUES (?, ?, ?)', location_data)
    insert_time = perf_counter() - start_time

    docs = [(random_doc_id(), public_key_id) for public_key_id, _, _ in location_data for _ in
            range(NUM_DOCUMENTS_PER_HOST)]

    start_time = perf_counter()
    conn.executemany('INSERT INTO document (doc_id, public_key_id) VALUES (?, ?)', docs)
    insert_time += perf_counter() - start_time

    return [doc_id for doc_id, _ in docs]


def perform_lookup(conn: Connection, _doc_ids: Deque[str]):
    _doc_ids.rotate()
    did = _doc_ids[0]
    response = conn.execute(QUERY, (did,)).fetchall()[0]
    print(print(response))


if __name__ == '__main__':
    print('file_size, public_keys, documents, query_rate')
    with TemporaryDirectory() as directory:
        directory = Path(directory)
        doc_ids = []
        db_location, db_conn = create_database(directory)
        for i in range(1, 16):
            for _ in range(i):
                doc_ids.extend(fill_database(db_conn))
            selected_doc_ids = deque(choice(doc_ids) for _ in range(NUM_TEST_QUERIES))
            timer = Timer(lambda: perform_lookup(db_conn, selected_doc_ids))
            elapsed = timer.timeit(NUM_TEST_QUERIES)
            num_records = db_conn.execute('select count(*) from document').fetchall()[0][0]
            num_pks = db_conn.execute('select count(*) from location').fetchall()[0][0]
            print(f'{getsize(db_location)}, {num_pks}, {num_records}, {NUM_TEST_QUERIES / elapsed}')
