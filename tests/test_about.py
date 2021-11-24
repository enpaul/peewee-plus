"""Test that metadata module matches pyproject"""
from pathlib import Path

import toml

import peewee_plus


def test_about():
    """Test metadata values"""

    with (Path(__file__).resolve().parent.parent / "pyproject.toml").open() as infile:
        pyproject = toml.load(infile)

    assert pyproject["tool"]["poetry"]["name"] == peewee_plus.__title__
    assert pyproject["tool"]["poetry"]["version"] == peewee_plus.__version__
    assert pyproject["tool"]["poetry"]["license"] == peewee_plus.__license__
    assert pyproject["tool"]["poetry"]["description"] == peewee_plus.__summary__
    assert pyproject["tool"]["poetry"]["repository"] == peewee_plus.__url__
    assert (
        all(
            item in peewee_plus.__authors__
            for item in pyproject["tool"]["poetry"]["authors"]
        )
        is True
    )
    assert (
        all(
            item in pyproject["tool"]["poetry"]["authors"]
            for item in peewee_plus.__authors__
        )
        is True
    )
