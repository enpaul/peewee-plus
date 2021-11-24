import uuid

import peewee
import pytest


@pytest.fixture(scope="function")
def fakedb(tmp_path):
    """Create a temporary pho-database (fakedb) for testing fields"""

    sqlite = peewee.SqliteDatabase(
        tmp_path / f"{uuid.uuid4()}.db",
        pragmas={
            "journal_mode": "wal",
            "cache_size": -1 * 64000,
            "foreign_keys": 1,
            "ignore_check_constraints": 0,
            "synchronous": 0,
        },
    )

    yield sqlite
