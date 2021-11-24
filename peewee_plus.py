from pathlib import Path
from typing import Optional

import peewee

__title__ = "peewee-plus"
__version__ = "0.1.0"
__license__ = "MIT"
__summary__ = "Various extensions, helpers, and utilities for Peewee"
__url__ = "https://github.com/enpaul/peewee-plus/"
__authors__ = ["Ethan Paul <24588726+enpaul@users.noreply.github.com>"]


__all__ = ["PathField", "PrecisionFloatField"]


class PathField(peewee.CharField):
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
        """Serialize a :class:`pathlib.Path` to a database string"""
        if value.is_absolute() and self.relative_to:
            value = value.relative_to(self.relative_to)
        return super().db_value(value)

    def python_value(self, value: str) -> Path:
        """Serialize a database string to a :class:`pathlib.path` object"""
        return (
            self.relative_to / Path(super().python_value(value))
            if self.relative_to
            else Path(super().python_value(value))
        )


class PrecisionFloatField(peewee.FloatField):
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
