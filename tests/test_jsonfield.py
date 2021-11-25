# pylint: disable=redefined-outer-name
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=unused-import
from pathlib import Path

import peewee
import pytest

import peewee_plus
from .fixtures import fakedb


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

    with pytest.raises(peewee.IntegrityError):
        bad = TestModel(some_data=Path("."))
        bad.save()
