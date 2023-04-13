# changelog

See also: [Github Release Page](https://github.com/enpaul/peewee-plus/releases).

## Version 1.2.1

View this release on: [Github](https://github.com/enpaul/peewee-plus/releases/tag/1.2.1),
[PyPI](https://pypi.org/project/peewee-plus/1.2.1/)

- Add PyPI classifier for Python 3.11
- Fix SQLite variable limit determination to account for changes in SQLite 3.32

## Version 1.2.0

View this release on: [Github](https://github.com/enpaul/peewee-plus/releases/tag/1.2.0),
[PyPI](https://pypi.org/project/peewee-plus/1.2.0/)

- Remove support for Python 3.6
- Update development workflows to use Poetry 1.2
- Fix nullable enums raising an `IntegrityError` when value is `None` (#1)

## Version 1.1.0

View this release on: [Github](https://github.com/enpaul/peewee-plus/releases/tag/1.1.0),
[PyPI](https://pypi.org/project/peewee-plus/1.1.0/)

- Add decorator function for wrapping callables in a flat database transaction

## Version 1.0.0

View this release on: [Github](https://github.com/enpaul/peewee-plus/releases/tag/1.0.0),
[PyPI](https://pypi.org/project/peewee-plus/1.0.0/)

- Add function for calculating SQLite batch size
- Add constants for SQLite default parameters
- Add field for storing JSON-serializable data
- Add field for storing Enums
- Add field for storing paths
- Add field for storing floats with custom precision parameters
