# pylint: disable=unused-import
# pylint: disable=redefined-outer-name
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
import peewee

import peewee_plus
from .fixtures import fakedb


# There isn't anything we can really test here since this field implements
# a MySQL-specific syntax and we test with SQLite. This test is here just
# to ensure that the behavior is consistent with the normal FloatField when
# working with an unsupported database backend
def test_compatibility(fakedb):
    """Check that the precision float field works on sqlite"""

    class TestModel(peewee.Model):
        class Meta:
            database = fakedb

        precise = peewee_plus.PrecisionFloatField(max_digits=7, decimal_places=3)
        imprecise = peewee.FloatField()

    fakedb.create_tables([TestModel])

    model = TestModel(precise=1234.567, imprecise=1234.567)
    model.save()

    model = TestModel.get()
    assert model.precise == model.imprecise
