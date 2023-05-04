# peewee+

Various extensions, helpers, and utilities for [Peewee](http://peewee-orm.com)

[![CI Status](https://github.com/enpaul/peewee-plus/workflows/CI/badge.svg?event=push)](https://github.com/enpaul/peewee-plus/actions)
[![PyPI Version](https://img.shields.io/pypi/v/peewee-plus)](https://pypi.org/project/peewee-plus/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/peewee-plus)](https://libraries.io/pypi/peewee-plus)
[![License](https://img.shields.io/pypi/l/peewee-plus)](https://opensource.org/licenses/MIT)
[![Python Supported Versions](https://img.shields.io/pypi/pyversions/peewee-plus)](https://www.python.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

See the [Changelog](https://github.com/enpaul/peewee-plus/blob/devel/CHANGELOG.md) for
release history.

## Documentation

*The documentation for this project is currently a work in progress. Please see the source
code for complete docs*

- [Installing](#installing)
- [Features](#features)
- [For Developers](#for-developers)

## Installing

peewee+ is [available on PyPI](https://pypi.org/project/peewee-plus/) and can be installed
using Poetry, Pipenv, or Pip:

```bash
# Using poetry
poetry add peewee-plus

# Using pipenv
pipenv install peewee-plus

# Using pip
python -m venv peewee
source peewee/bin/activate
python -m pip install peewee-plus
```

Once installed, Peewee+ can be imported like below:

```python
import peewee_plus
```

## Features

### Constants

`SQLITE_DEFAULT_PRAGMAS` - The default pragmas to use with an SQLite database connection,
taken directly from the
[Peewee docs](http://docs.peewee-orm.com/en/latest/peewee/database.html#recommended-settings).

`SQLITE_DEFAULT_VARIABLE_LIMIT` - The maximum number of variables an SQL query can use
when using SQLite

### Functions

`calc_batch_size` - Helper function for writing backend-agnostic batch queries while
accounting for the
[SQLite max variable limit](https://www.sqlite.org/limits.html#max_variable_number).

`flat_transaction` - Decorator function for wrapping callables in a database transaction
without creating nested transactions

### Classes

`PathField` - A Peewee database field for storing
[Pathlib](https://docs.python.org/3/library/pathlib.html) objects, optionally relative to
a runtime value.

`PrecisionFloatField` - A Peewee database field for storing floats while specifying the
[MySQL precision parameters](https://dev.mysql.com/doc/refman/8.0/en/floating-point-types.html)
`M` and `D`

`JSONField` - A Peewee database field for storing arbitrary JSON-serializable data

`EnumField` - A Peewee database field for storing Enums by name

`TimedeltaField` A Peewee database field for natively storing
[`datetime.timedelta`](https://docs.python.org/3/library/datetime.html#datetime.timedelta)
objects

## For Developers

All project contributors and participants are expected to adhere to the
[Contributor Covenant Code of Conduct, v2](CODE_OF_CONDUCT.md)
([external link](https://www.contributor-covenant.org/version/2/0/code_of_conduct/)).

The `devel` branch has the latest (and potentially unstable) changes. The stable releases
are tracked on [Github](https://github.com/enpaul/peewee-plus/releases),
[PyPi](https://pypi.org/project/peewee-plus/#history), and in the
[Changelog](CHANGELOG.md).

- To report a bug, request a feature, or ask for assistance, please
  [open an issue on the Github repository](https://github.com/enpaul/peewee-plus/issues/new).
- To report a security concern or code of conduct violation, please contact the project
  author directly at **‌me \[at‌\] enp dot‎ ‌one**.
- To submit an update, please
  [fork the repository](https://docs.github.com/en/enterprise/2.20/user/github/getting-started-with-github/fork-a-repo)
  and [open a pull request](https://github.com/enpaul/peewee-plus/compare).

Developing this project requires [Python 3.10](https://www.python.org/downloads/) or later
and [Poetry 1.2](https://python-poetry.org/docs/#installation) or later. GNU Make can
optionally be used to quickly setup a local development environment, but this is not
required.

To setup a local development environment:

```bash
# Clone the repository...
# ...over HTTPS
git clone https://github.com/enpaul/peewee-plus.git
# ...over SSH
git clone git@github.com:enpaul/peewee-plus.git

cd peewee-plus/

# Create and configure the local dev environment
make dev

# See additional make targets
make help
```
