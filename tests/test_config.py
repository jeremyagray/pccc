"""Config unit tests."""

import json
import os
import re
import shutil
import sys

import pytest

sys.path.insert(0, "/home/gray/src/work/pccc")

import pccc  # noqa: E402


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
def test_repr(fn, data, fs):
    """Test Config().__repr__()."""
    # TOML configuration file.
    fn_toml = re.sub(r"json$", "toml", fn)
    fs.create_file(fn_toml)
    with open(fn_toml, "w") as file:
        file.write(data["pyproject"])

    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load(["--config", fn_toml] + data["cli"])

    assert repr(ccr.options) == re.sub(r"\./pyproject\.toml", fn_toml, data["repr"])

    # JSON configuration file.
    fs.create_file(fn)
    with open(fn, "w") as file:
        json.dump(data, file, indent=2)

    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load(["--config", fn] + data["cli"])

    assert repr(ccr.options) == re.sub(r"\./pyproject\.toml", fn, data["repr"])


@pytest.mark.parametrize(
    "fn, data",
    load_configuration_data(),
)
def test_str(fn, data, fs):
    """Test Config().__str__()."""
    # TOML configuration file.
    fn_toml = re.sub(r"json$", "toml", fn)
    fs.create_file(fn_toml)
    with open(fn_toml, "w") as file:
        file.write(data["pyproject"])

    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load(["--config", fn_toml] + data["cli"])

    assert str(ccr.options) == data["str"]

    # JSON configuration file.
    fs.create_file(fn)
    with open(fn, "w") as file:
        json.dump(data, file, indent=2)

    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load(["--config", fn] + data["cli"])

    assert str(ccr.options) == data["str"]


@pytest.mark.parametrize(
    "fn, data",
    load_configuration_data(),
)
def test_validity(fn, data, fs):
    """Test Config().validate()."""
    # TOML configuration file.
    fn_toml = re.sub(r"json$", "toml", fn)
    fs.create_file(fn_toml)
    with open(fn_toml, "w") as file:
        file.write(data["pyproject"])

    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load(["--config", fn_toml] + data["cli"])

    if data["valid"]:
        assert ccr.options.validate() is True
    else:
        with pytest.raises(ValueError):
            ccr.options.validate()

    # JSON configuration file.
    fs.create_file(fn)
    with open(fn, "w") as file:
        json.dump(data, file, indent=2)

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
    actual = capsys.readouterr().out
    expected = "Unable to find configuration file .*, using defaults and CLI options."

    assert re.search(expected, actual)


# Fake file system with malformed configuration files.
def test_malformed_configuration_file(capsys, fs):
    """Test output with malformed configuration files."""
    ccr = pccc.ConventionalCommitRunner()

    # Write TOML file with JSON.
    fn = "./pyproject.toml"
    fs.create_file(fn)
    with open(fn, "w") as file:
        file.write('{"pccc": {}}')

    ccr.options.load("")

    capture = capsys.readouterr()

    error = "Ensure that file format matches extension"

    assert re.search(error, capture.out)

    # Write JSON file with TOML.
    fn = "./package.json"
    fs.create_file(fn)
    with open(fn, "w") as file:
        file.write("[tool.pccc]")

    ccr.options.load("")

    capture = capsys.readouterr()

    error = "Ensure that file format matches extension"

    assert re.search(error, capture.out)


def test_nonexistent_configuration_file(capsys):
    """Test output with non-existent configuration files."""
    files = [
        "no.toml",
        "no.json",
    ]

    for file in files:
        ccr = pccc.ConventionalCommitRunner()
        ccr.options.load(["--config", file])
        actual = capsys.readouterr().out
        expected = (
            f"Unable to find configuration file {file},"
            " using defaults and CLI options."
        )

        assert re.search(expected, actual)


def test_bad_configuration_files(capsys):
    """Test output with bad configuration files."""
    files = [
        "./tests/config/bad.toml",
        "./tests/config/bad.json",
    ]

    for file in files:
        ccr = pccc.ConventionalCommitRunner()
        ccr.options.load(["--config", file])
        actual = capsys.readouterr().out
        expected = "Ensure that file format matches extension"

        assert re.search(expected, actual)


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
