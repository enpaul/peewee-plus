import uuid

import peewee
import pytest

import peewee_plus


@pytest.fixture(scope="function")
def fakedb(tmp_path):
    """Create a temporary pho-database (fakedb) for testing fields"""

    sqlite = peewee.SqliteDatabase(
        str(tmp_path / f"{uuid.uuid4()}.db"),
        pragmas=peewee_plus.SQLITE_DEFAULT_PRAGMAS,
    )

    yield sqlite
