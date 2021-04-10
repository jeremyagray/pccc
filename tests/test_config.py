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
    actuals = []

    # TOML configuration file.
    fn_toml = re.sub(r"json$", "toml", fn)
    fs.create_file(fn_toml)
    with open(fn_toml, "w") as file:
        file.write(data["pyproject"])

    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load(["--config", fn_toml] + data["cli"])

    # actual = repr(ccr.options)
    actuals.append(
        {
            "string": repr(ccr.options),
            "fn": fn_toml,
        }
    )

    # JSON configuration file.
    fs.create_file(fn)
    with open(fn, "w") as file:
        json.dump(data, file, indent=2)

    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load(["--config", fn] + data["cli"])

    actuals.append(
        {
            "string": repr(ccr.options),
            "fn": fn,
        }
    )

    for actual in actuals:
        # Assertion on expectations for Config().__repr__().
        # repr begins with class name and open parenthesis.
        assert re.match(r"Config\(", actual["string"])
        # repr contains correct commit message.
        assert re.search(fr"\s*commit=\"{ccr.options.commit}\",\s+", actual["string"])
        # repr contains correct configuration file.
        assert re.search(fr"\s+config_file=\"{actual['fn']}\",\s+", actual["string"])
        # repr contains correct header length.
        assert re.search(
            fr"\s+header_length={ccr.options.header_length},\s+", actual["string"]
        )
        # repr contains correct body length.
        assert re.search(
            fr"\s+body_length={ccr.options.body_length},\s+", actual["string"]
        )
        # repr contains correct repair setting.
        assert re.search(fr"\s+repair={ccr.options.repair},\s+", actual["string"])
        # repr contains correct rewrap setting.
        assert re.search(fr"\s+rewrap={ccr.options.rewrap},\s+", actual["string"])
        # repr contains correct spell check setting.
        assert re.search(
            fr"\s+spell_check={ccr.options.spell_check},\s+", actual["string"]
        )
        # repr contains correct ignore generated commits setting.
        assert re.search(
            fr"\s+ignore_generated_commits={ccr.options.ignore_generated_commits},\s+",
            actual["string"],
        )

        # repr contains correct generated commits list.
        assert re.search(
            r",\s+generated_commits="
            fr"{re.escape(repr(ccr.options.generated_commits))},\s+",
            actual["string"],
        )
        # repr contains correct types list.
        assert re.search(
            fr",\s+types={re.escape(repr(ccr.options.types))},\s+", actual["string"]
        )
        # repr contains correct scopes list.
        assert re.search(
            fr",\s+scopes={re.escape(repr(ccr.options.scopes))},\s+", actual["string"]
        )
        # repr contains correct footers list.
        assert re.search(
            fr",\s+footers={re.escape(repr(ccr.options.footers))},\s+", actual["string"]
        )
        # repr contains correct required footers list.
        assert re.search(
            fr",\s+required_footers={re.escape(repr(ccr.options.required_footers))}\)",
            actual["string"],
        )

        # repr ends with close parenthesis.
        assert re.search(r"\)$", actual["string"])


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

    fs.create_file("str.toml")
    with open("str.toml", "w") as file:
        file.write(str(ccr.options))

    ccr2 = pccc.ConventionalCommitRunner()
    ccr2.options.load(["--config", "str.toml"] + data["cli"])

    assert str(ccr.options) == str(ccr2.options)

    # JSON configuration file.
    fs.create_file(fn)
    with open(fn, "w") as file:
        json.dump(data, file, indent=2)

    ccr3 = pccc.ConventionalCommitRunner()
    ccr3.options.load(["--config", fn] + data["cli"])

    assert str(ccr.options) == str(ccr3.options)
    assert str(ccr2.options) == str(ccr3.options)


@pytest.mark.parametrize(
    "fn, data",
    load_configuration_data(),
)
def test_config_validate(fn, data, fs):
    """Test Config().validate()."""
    files = []

    # TOML configuration file.
    fn = "config.toml"
    files.append(fn)
    fs.create_file(fn)
    with open(fn, "w") as f:
        f.write(data["pyproject"])

    # JSON configuration file.
    fn = "config.json"
    files.append(fn)
    fs.create_file(fn)
    with open(fn, "w") as f:
        json.dump(data, f, indent=2)

    # TOML in an unmarked file.
    fn = "config-one"
    files.append(fn)
    fs.create_file(fn)
    with open(fn, "w") as f:
        f.write(data["pyproject"])

    # JSON in an unmarked file.
    fn = "config-two"
    files.append(fn)
    fs.create_file(fn)
    with open(fn, "w") as f:
        json.dump(data, f, indent=2)

    for file in files:
        ccr = pccc.ConventionalCommitRunner()
        ccr.options.load(["--config", file] + data["cli"])

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

    # Both missing.
    actual = capsys.readouterr().out
    expected = "Unable to find configuration file .*, using defaults and CLI options."

    assert re.search(expected, actual)

    # TOML but no JSON.
    fn = "./pyproject.toml"
    fs.create_file(fn)
    with open(fn, "w") as file:
        file.write("[tool.pccc]")

    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load("")
    assert ccr.options.header_length == 50
    assert ccr.options.body_length == 72

    # JSON but no TOML.
    fs.remove_object(fn)
    fn = "./package.json"
    fs.create_file(fn)
    with open(fn, "w") as file:
        file.write('{"pccc": {}}')

    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load("")

    actual = capsys.readouterr().out

    expected = r"No such file or directory in the fake filesystem: \./pyproject\.toml"
    assert re.search(expected, actual)

    expected = r"trying package\.json\.\.\."
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

    # Garbage.
    fn = "hot-garbage"
    fs.create_file(fn)
    with open(fn, "w") as f:
        f.write("This file is hot garbage.\n")

    with pytest.raises(pccc.NotParseableError):
        ccr.options.load(["--config", fn])


def test_nonexistent_configuration_file(capsys):
    """Test output with non-existent configuration files."""
    files = [
        "no.toml",
        "no.json",
        "no.way",
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
