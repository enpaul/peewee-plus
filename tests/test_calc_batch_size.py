# pylint: disable=redefined-outer-name
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=unused-import
import peewee

import peewee_plus
from .fixtures import fakedb


def test_public_api():
    """Test that the public API components are exposed via ``__all__``"""

    assert peewee_plus.calc_batch_size.__name__ in peewee_plus.__all__
    assert peewee_plus.flat_transaction.__name__ in peewee_plus.__all__
    assert "SQLITE_DEFAULT_VARIABLE_LIMIT" in peewee_plus.__all__
    assert "SQLITE_DEFAULT_PRAGMAS" in peewee_plus.__all__


def test_sqlite(fakedb):
    """Test the calculation of batch sizes on SQLite"""

    class TestModel(peewee.Model):
        class Meta:
            database = fakedb

        data = peewee.IntegerField()

    # Three is just chosen as an arbitrary multiplier to ensure the value is larger than the
    # sqlite variable limit
    models = [
        TestModel(item) for item in range(peewee_plus.SQLITE_DEFAULT_VARIABLE_LIMIT * 3)
    ]
    assert (
        peewee_plus.calc_batch_size(models) <= peewee_plus.SQLITE_DEFAULT_VARIABLE_LIMIT
    )
    assert peewee_plus.calc_batch_size(models) < len(models)

    assert peewee_plus.calc_batch_size([]) == 0


def test_non_sqlite():
    """Test the calculation of batch sizes on non-SQLite"""

    class TestModel(peewee.Model):
        class Meta:
            database = peewee.DatabaseProxy()

        data = peewee.IntegerField()

    # Three is just chosen as an arbitrary multiplier to ensure the value is larger than the
    # sqlite variable limit
    assert peewee_plus.calc_batch_size(
        [
            TestModel(item)
            for item in range(peewee_plus.SQLITE_DEFAULT_VARIABLE_LIMIT * 3)
        ]
    ) == (peewee_plus.SQLITE_DEFAULT_VARIABLE_LIMIT * 3)
