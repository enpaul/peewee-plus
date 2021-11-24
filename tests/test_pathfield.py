# pylint: disable=redefined-outer-name
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=unused-import
from pathlib import Path

import peewee

import peewee_plus
from .fixtures import fakedb


def test_conversion(fakedb):
    """Test basic usage of PathField for roundtrip compatibility"""

    class TestModel(peewee.Model):
        class Meta:
            database = fakedb

        name = peewee.CharField()
        some_path = peewee_plus.PathField()

    fakedb.create_tables([TestModel])

    path1 = Path("foo", "bar", "baz")
    model1 = TestModel(name="one", some_path=path1)
    model1.save()

    model1 = TestModel.get(TestModel.name == "one")
    assert model1.some_path == path1
    assert not model1.some_path.is_absolute()

    path2 = Path("/etc", "fizz", "buzz")
    model2 = TestModel(name="two", some_path=path2)
    model2.save()

    model2 = TestModel.get(TestModel.name == "two")
    assert model2.some_path == path2
    assert model2.some_path.is_absolute()


def test_relative_to(fakedb):
    """Test usage of the ``relative_to`` parameter"""

    base_path = Path("/etc", "foobar")

    class TestModel(peewee.Model):
        class Meta:
            database = fakedb

        name = peewee.CharField()
        some_path = peewee_plus.PathField(relative_to=base_path)

    fakedb.create_tables([TestModel])

    path1 = Path("foo", "bar", "baz")
    model1 = TestModel(name="one", some_path=path1)
    model1.save()

    model1 = TestModel.get(TestModel.name == "one")
    assert model1.some_path.is_absolute()
    assert model1.some_path == base_path / path1

    path2 = Path("fizz", "buzz")
    model2 = TestModel(name="two", some_path=base_path / path2)
    model2.save()

    model2 = TestModel.get(TestModel.name == "two")
    assert model2.some_path.is_absolute()
    assert model2.some_path == base_path / path2
