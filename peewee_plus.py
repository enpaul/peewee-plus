"""Peewee+

:constant SQLITE_DEFAULT_VARIABLE_LIMIT: The default number of variables that a single SQL query
                                         can contain when interfacing with SQLite. The actual
                                         number is set at compile time and is not easily
                                         discoverable from within Python. This default value will
                                         be correct for the vast majority of applications.

:constant SQLITE_DEFAULT_PRAGMAS: The default pragmas that should be used when instantiating an
                                  SQLite database connection. The value for this constant is taken
                                  directly from the `Peewee documentation`_

.. _`Peewee documentation`: http://docs.peewee-orm.com/en/latest/peewee/database.html#recommended-settings
"""
import contextlib
import enum
import functools
import json
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Type
from typing import TypeVar

import peewee


__title__ = "peewee-plus"
__version__ = "1.2.0"
__license__ = "MIT"
__summary__ = "Various extensions, helpers, and utilities for Peewee"
__url__ = "https://github.com/enpaul/peewee-plus/"
__authors__ = ["Ethan Paul <24588726+enpaul@users.noreply.github.com>"]


__all__ = [
    "__title__",
    "__version__",
    "__license__",
    "__summary__",
    "__url__",
    "__authors__",
    "calc_batch_size",
    "EnumField",
    "flat_transaction",
    "JSONField",
    "PathField",
    "PrecisionFloatField",
    "SQLITE_DEFAULT_PRAGMAS",
    "SQLITE_DEFAULT_VARIABLE_LIMIT",
]


SQLITE_DEFAULT_PRAGMAS: Dict[str, Any] = {
    "journal_mode": "wal",
    "cache_size": -1 * 64000,
    "foreign_keys": 1,
    "ignore_check_constraints": 0,
    "synchronous": 0,
}


SQLITE_DEFAULT_VARIABLE_LIMIT: int = 999


T = TypeVar("T", bound=peewee.Model)


def calc_batch_size(
    models: Sequence[T], sqlite_variable_limit: int = SQLITE_DEFAULT_VARIABLE_LIMIT
) -> int:
    """Determine the batch size that should be used when performing queries

    This is intended to work around the query variable limit in SQLite. Critically this is a
    limit to the number of _variables_, not _records_ that can be referenced in a single query.

    The "correct" way to calculate this is to iterate over the model list and tally the number of
    changed fields, then add one for the table name, and each time you reach the
    ``SQLITE_VARIABLE_LIMIT`` (which is a known constant) cut a new batch until all the models are
    processed. This is very complicated because peewee doesn't provide a simple way to reliably
    identify changed fields.

    The naive way to calculate this (i.e. the way this function does it) is to determine the
    maximum number of variables that _could be_ used to modify a record and use that as the
    constant batch limiter. The theoretical maximum number of variables associated with a single
    record is equal to the number of fields on that record, plus 1 (for the table name). This
    gives the batch size (i.e. number of records that can be modified in a single query) as:

    ::

      999 / (len(fields) + 1)

    Where ``fields`` is an array of the fields that could be written on the record.

    Example usage:

    .. code-block:: python

        models = [MyModel(...), MyModel(...), MyModel(...), MyModel(...)]

        with database.atomic():
            MyModel.bulk_create(models, batch_size=calc_batch_size(models))

    .. note:: This function (pretty safely) requires that all the records in ``models`` are all
              instances of the same model.

    .. note:: This function just returns ``len(models)`` if the backend is anything other than
              :class:`peewee.SqliteDatabase`. This is because the limitation this function works
              around is only applicable to SQLite, so on other platforms the batch size can just
              be as large as possible. This also helps to support writing code that transparently
              supports multiple backends.

    :param models: Sequence of models to be created or updated that need to be batched
    :param sqlite_variable_limit: Number of variables that can be present in a single SQL query;
                                  this is defined at compile time in the SQLite bindings for the
                                  current platform and should not need to be changed unless using
                                  SQLite bindings that were compiled with custom parameters.
    :returns: Number of models that can be processed in a single batch
    """
    # We need to inspect the models in the logic below, so if there are no models then just
    # return zero since the batch size doesn't matter anyway
    if not models:
        return 0
    if isinstance(
        models[0]._meta.database,  # pylint: disable=protected-access
        peewee.SqliteDatabase,
    ):
        return int(
            sqlite_variable_limit
            / (len(models[0]._meta.fields) + 1)  # pylint: disable=protected-access
        )
    return len(models)


def flat_transaction(interface: peewee.Database):
    """Database transaction wrapper that avoids nested transactions

    A decorator that can be used to decorate functions or methods so that the entire callable
    is executed in a single transaction context. If a transaction is already open then it will
    be reused rather than opening a nested transaction.

    Example usage:

    .. code-block:: python

      db = peewee.SqliteDatabase("test.db")


      @flat_transaction(db)
      def subquery():
          ...


      @flat_transaction(db)
      def my_query():
          ...
          subquery()


      # This call opens only a single transaction
      my_query()

    :param interface: Peewee database interface that should be used to open the transaction
    """

    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            with interface.atomic() if not interface.in_transaction() else contextlib.nullcontext():
                return func(*args, **kwargs)

        return inner

    return outer


# TODO: The disable=abstract-method pragmas below are to get around new linting warnings
# in pylint>2.12, but they haven't been addressed properly. They should be revisited
# and fixed properly in the future.
class PathField(peewee.CharField):  # pylint: disable=abstract-method
    """Field class for storing file paths

    This field can be used to simply store pathlib paths in the database without needing to
    cast to ``str`` on write and ``Path`` on read.

    It can also serve to save paths relative to a root path defined at runtime. This can be
    useful when an application stores files under a directory defined in the app configuration,
    such as in an environment variable or a config file.

    For example, if a model is defined like below to load a path from the ``MYAPP_DATA_DIR``
    environment variable:

    .. code-block:: python

        class MyModel(peewee.Model):
            some_path = peewee_plus.PathField(relative_to=Path(os.environ["MYAPP_DATA_DIR"]))


        p1 = MyModel(some_path=Path(os.environ["MYAPP_DATA_DIR"]) / "foo.json").save()
        p2 = MyModel(some_path=Path("bar.json")).save()

    Then the data directory can be changed without updating the database, and the code can
    still rely on the database always returning absolute paths:

    ::

        >>> os.environ["MYAPP_DATA_DIR"] = "/etc/myapp"
        >>> [item.some_path for item in MyModel.select()]
        [PosixPath('/etc/myapp/foo.json'), PosixPath('/etc/myapp/bar.json')]
        >>>
        >>> os.environ["MYAPP_DATA_DIR"] = "/opt/myapp/data"
        >>> [item.some_path for item in MyModel.select()]
        [PosixPath('/opt/myapp/data/foo.json'), PosixPath('/opt/myapp/data/bar.json')]
        >>>

    :param relative_to: Optional root path that paths should be stored relative to. If specified
                        then values being set will be converted to relative paths under this path,
                        and values being read will always be absolute paths under this path.
    """

    def __init__(self, *args, relative_to: Optional[Path] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.relative_to = relative_to

    def db_value(self, value: Path) -> str:
        if value.is_absolute() and self.relative_to:
            value = value.relative_to(self.relative_to)
        return super().db_value(value)

    def python_value(self, value: str) -> Path:
        return (
            self.relative_to / Path(super().python_value(value))
            if self.relative_to
            else Path(super().python_value(value))
        )


class PrecisionFloatField(peewee.FloatField):  # pylint: disable=abstract-method
    """Field class for storing floats with custom precision parameters

    This field adds support for specifying the ``M`` and ``D`` precision parameters of a
    ``FLOAT`` field as specified in the `MySQL documentation`_.
    accepts. See the `MySQL docs`_ for more information.

    .. warning:: This field implements syntax that is specific to MySQL. When used with a
                 different database backend, such as SQLite or Postgres, it behaves identically
                 to :class:`peewee.FloatField`

    .. note:: This field's implementation was adapted from here_

    .. _`MySQL documentation`: https://dev.mysql.com/doc/refman/8.0/en/floating-point-types.html
    .. _here: https://stackoverflow.com/a/67476045/5361209

    :param max_digits: Maximum number of digits, combined from left and right of the decimal place,
                       to store for the value.
    :param decimal_places: Maximum number of digits that will be stored after the decimal place
    """

    def __init__(self, *args, max_digits: int = 10, decimal_places: int = 4, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_digits = max_digits
        self.decimal_places = decimal_places

    def get_modifiers(self):
        return [self.max_digits, self.decimal_places]


class JSONField(peewee.TextField):  # pylint: disable=abstract-method
    """Field class for storing JSON-serializable data

    This field can be used to store a dictionary of data directly in the database without needing
    without needing to call :func:`json.dumps` and :func:`json.loads` directly.

    ::

        >>> class MyModel(peewee.Model):
        ...    some_data = JSONField()
        ...
        >>> m = MyModel(some_data={"foo": 1, "bar": 2})
        >>> m.save()
        >>> m.some_data
        {'foo': 1, 'bar': 2}
        >>>

    .. warning:: If a non-JSON serializable object is set to the field then a
                 :err:`peewee.IntegrityError` will be raised

    .. warning:: This is a very bad way to store data in a RDBMS and effectively makes the data
                 contained in the field unqueriable.

    :param dump_params: Additional keyword arguments to unpack into :func:`json.dump`
    :param load_params: Additional keyword arguments to unpack into :func:`json.load`
    """

    def __init__(
        self,
        *args,
        dump_params: Optional[Dict[str, Any]] = None,
        load_params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.dump_params = dump_params or {}
        self.load_params = load_params or {}

    def db_value(self, value: Any) -> str:
        try:
            return super().db_value(json.dumps(value, **self.dump_params))
        except TypeError as err:
            raise peewee.IntegrityError(
                f"Failed to JSON encode object of type '{type(value)}'"
            ) from err

    def python_value(self, value: str) -> Any:
        try:
            return json.loads(super().python_value(value), **self.load_params)
        except json.JSONDecodeError as err:
            raise peewee.IntegrityError(
                f"Failed to decode JSON value from database column '{self.column}'"
            ) from err


class EnumField(peewee.CharField):  # pylint: disable=abstract-method
    """Field class for storing Enums

    This field can be used for storing members of an :class:`enum.Enum` in the database,
    effectively storing a database reference to a value defined in the application.

    .. warning:: This field ties database data to application structure: if the Enum passed
                 to this field is modified then the application may encounter errors when
                 trying to interface with the database schema.

    ::

        >>> class MyOptions(enum.Enum):
        ...    FOO = "have you ever heard the tragedy"
        ...    BAR = "of darth plageius"
        ...    BAZ = "the wise?"
        ...
        >>>
        >>> class MyModel(peewee.Model):
        ...    option = EnumField(MyOptions)
        ...
        >>> m = MyModel(option=MyOptions.FOO)
        >>> m.save()
        >>> m.option
        <MyOptions.FOO: "have you ever heard the tragedy">
        >>>

    :param enumeration: The Enum to accept members of and to use for decoding database values
    :raises TypeError: If the value to be written to the field is not a member of the
                       specified Enum
    :raises peewee.IntegrityError: If the value read back from the database cannot be decoded to
                                   a member of the specified Enum
    """

    def __init__(self, enumeration: Type[enum.Enum], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enumeration = enumeration

    def db_value(self, value: enum.Enum) -> str:
        if not isinstance(value, self.enumeration):
            raise TypeError(f"Enum {self.enumeration.__name__} has no value '{value}'")
        return super().db_value(value.name)

    def python_value(self, value: str) -> enum.Enum:
        try:
            return (
                None
                if value is None and self.null
                else self.enumeration[super().python_value(value)]
            )
        except KeyError:
            raise peewee.IntegrityError(
                f"Enum {self.enumeration.__name__} has no value with name '{value}'"
            ) from None
