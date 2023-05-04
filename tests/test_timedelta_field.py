# pylint: disable=redefined-outer-name
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=unused-import
import datetime
from pathlib import Path

import peewee

import peewee_plus
from .fixtures import fakedb


def test_public_api():
    """Test that the public API components are exposed via ``__all__``"""

    assert peewee_plus.TimedeltaField.__name__ in peewee_plus.__all__


def test_conversion(fakedb):
    """Test basic usage of PathField for roundtrip compatibility"""

    class TestModel(peewee.Model):
        class Meta:
            database = fakedb

        name = peewee.CharField()
        some_timedelta = peewee_plus.TimedeltaField()

    fakedb.create_tables([TestModel])

    delta = datetime.timedelta(seconds=300)
    model = TestModel(name="one", some_timedelta=delta)
    model.save()

    new = TestModel.get(TestModel.name == "one")
    assert new.some_timedelta == delta
