"""Config unit tests."""

import json
import os
import re
import shutil
import sys

import pytest

sys.path.insert(0, "/home/gray/src/work/pccc")

import pccc  # noqa: E402


def setup_module():
    """Generate files from testing data JSON files.

    Currently, this produces a ``*.toml`` file from the ``pyproject``
    field of the ``*.json`` file.
    """
    json_file_re = re.compile(r"\d{4}\.json$")

    with os.scandir("./tests/config") as dir:
        for entry in dir:
            if entry.is_file() and json_file_re.match(entry.name):
                with open(entry.path, "r") as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError as error:
                        print(f"JSON error in file {file}")
                        raise error

                toml_fn = re.sub(r"json$", "toml", entry.path)
                with open(toml_fn, "w") as file:
                    file.write(data["pyproject"])


def load_configuration_data():
    """Load configuration data for testing."""
    data = []
    json_file_re = re.compile(r"\d{4}\.json$")

    with os.scandir("./tests/config") as dir:
        for entry in dir:
            if entry.is_file() and json_file_re.match(entry.name):
                with open(entry.path, "r") as file:
                    try:
                        datum = json.load(file)
                    except json.JSONDecodeError as error:
                        print(f"JSON error in file {entry.name}")
                        raise error
                data.append(tuple([entry.path, datum]))

    return tuple(data)


@pytest.mark.parametrize(
    "fn, data",
    load_configuration_data(),
)
def test_repr(fn, data):
    """Test Config().__repr__()."""
    # TOML configuration file.
    ccr = pccc.ConventionalCommitRunner()
    file = re.sub(r"json$", "toml", fn)
    ccr.options.load(["--config", file] + data["cli"])

    assert repr(ccr.options) == re.sub(r"\./pyproject\.toml", file, data["repr"])

    # JSON configuration file.
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load(["--config", fn] + data["cli"])

    assert repr(ccr.options) == re.sub(r"\./pyproject\.toml", fn, data["repr"])


@pytest.mark.parametrize(
    "fn, data",
    load_configuration_data(),
)
def test_str(fn, data):
    """Test Config().__str__()."""
    # TOML configuration file.
    ccr = pccc.ConventionalCommitRunner()
    file = re.sub(r"json$", "toml", fn)
    ccr.options.load(["--config", file] + data["cli"])

    assert str(ccr.options) == data["str"]

    # JSON configuration file.
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load(["--config", fn] + data["cli"])

    assert str(ccr.options) == data["str"]


@pytest.mark.parametrize(
    "fn, data",
    load_configuration_data(),
)
def test_validity(fn, data):
    """Test Config().validate()."""
    # TOML configuration file.
    ccr = pccc.ConventionalCommitRunner()
    file = re.sub(r"json$", "toml", fn)
    ccr.options.load(["--config", file] + data["cli"])

    if data["valid"]:
        assert ccr.options.validate() is True
    else:
        with pytest.raises(ValueError):
            ccr.options.validate()

    # JSON configuration file.
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load(["--config", fn] + data["cli"])

    assert repr(ccr.options) == re.sub(r"\./pyproject\.toml", fn, data["repr"])

    if data["valid"]:
        assert ccr.options.validate() is True
    else:
        with pytest.raises(ValueError):
            ccr.options.validate()


# Fake file system without pyproject.toml/package.json.
def test_nonexistent_default_files(capsys, fs):
    """Test output with non-existent default configuration files."""
    ccr = pccc.ConventionalCommitRunner()

    ccr.options.load("")

    capture = capsys.readouterr()

    error = "Unable to find configuration file .*, using defaults and CLI options."

    assert re.search(error, capture.out)


# Fake file system with malformed pyproject.toml.
def test_bad_default_toml_file(capsys, fs):
    """Test output with a malformed TOML default configuration file."""
    ccr = pccc.ConventionalCommitRunner()

    fn = "./pyproject.toml"
    fs.create_file(fn)
    with open(fn, "w") as file:
        file.write('{"pccc": {}}')

    ccr.options.load("")

    capture = capsys.readouterr()

    error = "Ensure that file format matches extension"

    assert re.search(error, capture.out)


# Fake file system with malformed pyproject.toml.
def test_bad_default_json_file(capsys, fs):
    """Test output with a malformed JSON default configuration file."""
    ccr = pccc.ConventionalCommitRunner()

    fn = "./package.json"
    fs.create_file(fn)
    with open(fn, "w") as file:
        file.write("[tool.pccc]")

    ccr.options.load("")

    capture = capsys.readouterr()

    error = "Ensure that file format matches extension"

    assert re.search(error, capture.out)


def test_nonexistent_toml_file(capsys):
    """Test output with a non-existent TOML configuration file."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load(["--config", "no.toml"])

    capture = capsys.readouterr()

    error = (
        "Unable to find configuration file no.toml," " using defaults and CLI options."
    )

    assert re.search(error, capture.out)


def test_nonexistent_json_file(capsys):
    """Test output with a non-existent JSON configuration file."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load(["--config", "no.json"])
    capture = capsys.readouterr()

    error = (
        "Unable to find configuration file no.json," " using defaults and CLI options."
    )

    assert re.search(error, capture.out)


def test_bad_toml_file(capsys):
    """Test output with a malformed TOML configuration file."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load(["--config", "./tests/config/bad.toml"])

    capture = capsys.readouterr()

    error = "Ensure that file format matches extension"

    assert re.search(error, capture.out)


def test_bad_json_file(capsys):
    """Test output with a malformed JSON configuration file."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load(["--config", "./tests/config/bad.json"])

    capture = capsys.readouterr()

    error = "Ensure that file format matches extension"

    assert re.search(error, capture.out)


def test_show_license_info(capsys):
    """Test ``--show-license`` and ``--show-warranty`` CLI options."""
    expected = """\
pccc:  The Python Conventional Commit Checker.

Copyright (C) 2021 Jeremy A Gray <jeremy.a.gray@gmail.com>.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

    with pytest.raises(SystemExit):
        ccr = pccc.ConventionalCommitRunner()
        ccr.options.load(["--show-license"])

        actual = capsys.readouterr().out

        assert actual == expected

    with pytest.raises(SystemExit):
        ccr = pccc.ConventionalCommitRunner()
        ccr.options.load(["--show-warranty"])

        actual = capsys.readouterr().out

        assert actual == expected
