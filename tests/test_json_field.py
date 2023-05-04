# pylint: disable=redefined-outer-name
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=unused-import
from pathlib import Path

import peewee
import pytest

import peewee_plus
from .fixtures import fakedb


def test_public_api():
    """Test that the public API components are exposed via ``__all__``"""

    assert peewee_plus.JSONField.__name__ in peewee_plus.__all__


def test_json(fakedb):
    """Test basic usage of JSONField class"""

    class TestModel(peewee.Model):
        class Meta:
            database = fakedb

        some_data = peewee_plus.JSONField()

    fakedb.create_tables([TestModel])

    data = {"foo": 10, "bar": ["hello", "world"], "baz": True}

    model = TestModel(some_data=data)
    model.save()

    model = TestModel.get()
    assert model.some_data == data


def test_errors(fakedb):
    """Test that errors are raised as expected"""

    class GoodModel(peewee.Model):
        class Meta:
            database = fakedb
            # Needs to match the table name below
            table_name = "one_table"

        id = peewee.AutoField()
        some_data = peewee_plus.JSONField()

    class BadModel(peewee.Model):
        class Meta:
            database = fakedb
            # Needs to match the table name above
            table_name = "one_table"

        id = peewee.AutoField()
        some_data = peewee.TextField()

    fakedb.create_tables([GoodModel])

    with pytest.raises(ValueError):
        # The usage of path here is arbitrary, it just needs to be any
        # non-JSON serializable type
        bad = GoodModel(some_data=Path("."))
        bad.save()

    good = GoodModel(some_data={"foo": 123})
    good.save()

    # This is overwriting the ``some_data`` on the above object with garbage
    bad = BadModel.get(good.id)
    bad.some_data = "This{ string' is not, valid JSON;"
    bad.save()

    with pytest.raises(peewee.IntegrityError):
        GoodModel.get(good.id)
