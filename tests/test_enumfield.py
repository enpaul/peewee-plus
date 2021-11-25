# pylint: disable=redefined-outer-name
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=unused-import
import enum

import peewee
import pytest

import peewee_plus
from .fixtures import fakedb


def test_enum(fakedb):
    """Test basic functionality of the enum field"""

    class TestEnum(enum.Enum):
        FOO = "fizz"
        BAR = "buzz"

    class TestModel(peewee.Model):
        class Meta:
            database = fakedb

        data = peewee_plus.EnumField(TestEnum)

    fakedb.create_tables([TestModel])

    model = TestModel(data=TestEnum.FOO)
    model.save()

    model = TestModel.get()
    assert model.data == TestEnum.FOO

    class ModifiedEnum(enum.Enum):
        BAR = "buzz"

    class ModifiedModel(peewee.Model):
        class Meta:
            table_name = TestModel._meta.table_name  # pylint: disable=protected-access
            database = fakedb

        data = peewee_plus.EnumField(ModifiedEnum)

    with pytest.raises(peewee.IntegrityError):
        ModifiedModel.get()

    class BadEnum(enum.Enum):
        NOTHING = "nowhere"

    with pytest.raises(TypeError):
        bad = TestModel(data=BadEnum.NOTHING)
        bad.save()
