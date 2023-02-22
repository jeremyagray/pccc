# ******************************************************************************
#
# pccc, the Python Conventional Commit Checker.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2020-2023 Jeremy A Gray <gray@flyquackswim.com>.
#
# ******************************************************************************

"""Config unit tests."""

import json
import os
import re
import sys

import bespon
import pytest
import toml
from hypothesis import given
from hypothesis import strategies as st
from ruamel.yaml import YAML

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


def tomlify_list(list):
    """Stringify a list as ``toml.dumps()`` would."""
    if list:
        return '[ "' + '", "'.join(list) + '",]'
    else:
        return "[]"


@st.composite
def configuration(draw):
    """Generate a configuration object strategy."""
    footers = draw(
        st.lists(
            st.text(
                st.characters(
                    whitelist_categories=("L", "N"),
                    blacklist_categories=("C"),
                ),
                min_size=3,
                max_size=10,
            ),
            unique=True,
        )
    )

    return pccc.Config(
        header_length=draw(st.integers(min_value=50, max_value=50)),
        body_length=draw(st.integers(min_value=70, max_value=120)),
        repair=draw(st.booleans()),
        wrap=draw(st.booleans()),
        force_wrap=draw(st.booleans()),
        spell_check=draw(st.booleans()),
        ignore_generated_commits=draw(st.booleans()),
        generated_commits=draw(
            st.lists(
                st.text(
                    st.characters(
                        whitelist_categories=("L", "N", "P"),
                        blacklist_categories=("C"),
                    ),
                    min_size=3,
                    max_size=10,
                ),
                unique=True,
            )
        ),
        types=draw(
            st.lists(
                st.text(
                    st.characters(
                        whitelist_categories=("L", "N"),
                        blacklist_categories=("C"),
                    ),
                    min_size=3,
                    max_size=10,
                ),
                unique=True,
            )
        ),
        scopes=draw(
            st.lists(
                st.text(
                    st.characters(
                        whitelist_categories=("L", "N"),
                        blacklist_categories=("C"),
                    ),
                    min_size=3,
                    max_size=10,
                ),
                unique=True,
            )
        ),
        footers=footers,
        required_footers=footers,
    )


@given(conf=configuration())
def test_stringify_config(conf):
    """Should stringify a config."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options = conf

    # Assert the TOML is correct.
    assert f"header_length = {conf.header_length}" in str(ccr.options)
    assert f"body_length = {conf.body_length}" in str(ccr.options)
    assert f"repair = {str(conf.repair).lower()}" in str(ccr.options)
    assert f"wrap = {str(conf.wrap).lower()}" in str(ccr.options)
    assert f"force_wrap = {str(conf.force_wrap).lower()}" in str(ccr.options)
    assert f"spell_check = {str(conf.spell_check).lower()}" in str(ccr.options)
    assert (
        f"ignore_generated_commits = {str(conf.ignore_generated_commits).lower()}"
        in str(ccr.options)
    )
    assert f"types = {tomlify_list(conf.types)}" in str(ccr.options)

    # Assert the JSON is correct.
    ccr.options.set_format("JSON")
    assert f'"header_length": {conf.header_length}' in str(ccr.options)
    assert f'"body_length": {conf.body_length}' in str(ccr.options)
    assert f'"repair": {str(conf.repair).lower()}' in str(ccr.options)
    assert f'"wrap": {str(conf.wrap).lower()}' in str(ccr.options)
    assert f'"force_wrap": {str(conf.force_wrap).lower()}' in str(ccr.options)
    assert f'"spell_check": {str(conf.spell_check).lower()}' in str(ccr.options)
    assert (
        f'"ignore_generated_commits": {str(conf.ignore_generated_commits).lower()}'
        in str(ccr.options)
    )


@given(conf=configuration())
def test_reproduce_config(conf):
    """Should reproduce a config."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options = conf

    # Assert on the repr().
    assert f"header_length={conf.header_length}" in repr(ccr.options)
    assert f"body_length={conf.body_length}" in repr(ccr.options)
    assert f"repair={conf.repair}" in repr(ccr.options)
    assert f"wrap={conf.wrap}" in repr(ccr.options)
    assert f"force_wrap={conf.force_wrap}" in repr(ccr.options)
    assert f"spell_check={conf.spell_check}" in repr(ccr.options)
    assert f"ignore_generated_commits={conf.ignore_generated_commits}" in repr(
        ccr.options
    )
    assert f"types={conf.types}" in repr(ccr.options)
    assert f"scopes={conf.scopes}" in repr(ccr.options)


# FIXME
@pytest.mark.parametrize(
    "fn, data",
    load_configuration_data(),
)
def test_str_repr_property(fn, data, fs):
    """Should not change depending on source format.

    Test ``Config().__str__()`` and ``Config().__repr__()`` by writing
    and loading the fixture data created to each other using TOML,
    JSON, TOML then JSON, and JSON then TOML and then comparing both
    the strings written and the objects.
    """
    # Use the fixture's JSON to write a TOML file, then load the TOML
    # and write a second file.  Then, assert that the two ``Config()``
    # objects have equal reproductions and string representations.
    fn = "one.toml"
    fs.create_file(fn)
    with open(fn, "w") as f:
        tdata = {"pccc": data["pccc"]}
        toml.dump(tdata, f)

    ccr_one = pccc.ConventionalCommitRunner()
    ccr_one.options.load(["--config", fn] + data["cli"])
    fs.remove_object(fn)

    fn = "two.toml"
    fs.create_file(fn)
    with open(fn, "w") as f:
        f.write(str(ccr_one.options))

    ccr_two = pccc.ConventionalCommitRunner()
    ccr_two.options.load(["--config", fn] + data["cli"])
    fs.remove_object(fn)

    # Assert ``Config().__repr__()`` are equal.
    ccr_one.options.set_format("TOML")
    ccr_two.options.set_format("TOML")
    assert repr(ccr_one.options) == re.sub(
        r"two\.toml", "one.toml", repr(ccr_two.options)
    )

    # Assert ``Config().__str__()`` are equal.
    ccr_one.options.set_format("TOML")
    ccr_two.options.set_format("TOML")
    assert str(ccr_one.options) == str(ccr_two.options)
    ccr_one.options.set_format("JSON")
    ccr_two.options.set_format("JSON")
    assert str(ccr_one.options) == str(ccr_two.options)

    # Use the fixture's JSON to write a JSON file, then load the JSON
    # and write a second file.  Then, assert that the two ``Config()``
    # objects have equal reproductions and string representations.
    fn = "one.json"
    fs.create_file(fn)
    with open(fn, "w") as f:
        json.dump({"pccc": data["pccc"]}, f, indent=2)

    ccr_three = pccc.ConventionalCommitRunner()
    ccr_three.options.load(["--config", fn] + data["cli"])
    fs.remove_object(fn)

    fn = "two.json"
    fs.create_file(fn)
    with open(fn, "w") as f:
        ccr_three.options.set_format("JSON")
        f.write(str(ccr_three.options))

    ccr_four = pccc.ConventionalCommitRunner()
    ccr_four.options.load(["--config", fn] + data["cli"])
    fs.remove_object(fn)

    # Assert ``Config().__repr__()`` are equal.
    ccr_three.options.set_format("TOML")
    ccr_four.options.set_format("TOML")
    assert repr(ccr_three.options) == re.sub(
        r"two\.json", "one.json", repr(ccr_four.options)
    )

    # Assert ``Config().__str__()`` are equal.
    ccr_three.options.set_format("TOML")
    ccr_four.options.set_format("TOML")
    assert str(ccr_three.options) == str(ccr_four.options)
    ccr_three.options.set_format("JSON")
    ccr_four.options.set_format("JSON")
    assert str(ccr_three.options) == str(ccr_four.options)

    # Mixed case:  TOML, then JSON.
    fn = "one.toml"
    fs.create_file(fn)
    with open(fn, "w") as f:
        toml.dump({"pccc": data["pccc"]}, f)

    ccr_one = pccc.ConventionalCommitRunner()
    ccr_one.options.load(["--config", fn] + data["cli"])
    fs.remove_object(fn)

    fn = "two.json"
    fs.create_file(fn)
    with open(fn, "w") as f:
        ccr_one.options.set_format("JSON")
        f.write(str(ccr_one.options))

    ccr_two = pccc.ConventionalCommitRunner()
    ccr_two.options.load(["--config", fn] + data["cli"])
    fs.remove_object(fn)

    # Assert ``Config().__repr__()`` are equal.
    ccr_one.options.set_format("TOML")
    ccr_two.options.set_format("TOML")
    assert repr(ccr_one.options) == re.sub(
        r"two\.json", "one.toml", repr(ccr_two.options)
    )

    # Assert ``Config().__str__()`` are equal.
    ccr_one.options.set_format("TOML")
    ccr_two.options.set_format("TOML")
    assert str(ccr_one.options) == str(ccr_two.options)
    ccr_one.options.set_format("JSON")
    ccr_two.options.set_format("JSON")
    assert str(ccr_one.options) == str(ccr_two.options)

    # Mixed case:  JSON, then TOML.
    fn = "one.json"
    fs.create_file(fn)
    with open(fn, "w") as f:
        json.dump({"pccc": data["pccc"]}, f, indent=2)

    ccr_one = pccc.ConventionalCommitRunner()
    ccr_one.options.load(["--config", fn] + data["cli"])
    fs.remove_object(fn)

    fn = "two.toml"
    fs.create_file(fn)
    with open(fn, "w") as f:
        ccr_one.options.set_format("TOML")
        f.write(str(ccr_one.options))

    ccr_two = pccc.ConventionalCommitRunner()
    ccr_two.options.load(["--config", fn] + data["cli"])
    fs.remove_object(fn)

    # Assert ``Config().__repr__()`` are equal.
    ccr_one.options.set_format("TOML")
    ccr_two.options.set_format("TOML")
    assert repr(ccr_one.options) == re.sub(
        r"two\.toml", "one.json", repr(ccr_two.options)
    )

    # Assert ``Config().__str__()`` are equal.
    ccr_one.options.set_format("TOML")
    ccr_two.options.set_format("TOML")
    assert str(ccr_one.options) == str(ccr_two.options)
    ccr_one.options.set_format("JSON")
    ccr_two.options.set_format("JSON")
    assert str(ccr_one.options) == str(ccr_two.options)


@pytest.mark.parametrize(
    "fn, data",
    load_configuration_data(),
)
def test_config_validate(fn, data, fs):
    """Test Config().validate()."""
    files = []

    # TOML files.
    toml_files = [
        "pyproject.toml",
        "config.toml",
        "config-one",
    ]

    for file in toml_files:
        files.append(file)
        fs.create_file(file)
        with open(file, "w") as f:
            if "pyproject.toml" not in file:
                data["pyproject"] = re.sub(
                    r"\[tool\.pccc\]", "[pccc]", data["pyproject"]
                )
            f.write(data["pyproject"])

    # JSON files.
    json_files = [
        "package.json",
        "config.json",
        "config-two",
    ]

    for file in json_files:
        files.append(file)
        fs.create_file(file)
        with open(file, "w") as f:
            json.dump(data, f, indent=2)

    for file in files:
        ccr = pccc.ConventionalCommitRunner()
        ccr.options.load(["--config", file] + data["cli"])

        if data["valid"]:
            assert ccr.options.validate() is True
        else:
            with pytest.raises(ValueError):
                ccr.options.validate()


# Create files with different body lengths and test the correct one is
# loaded.
def test_config_file_loading_order(fs):
    """Should load configuration files in correct order."""
    i = 60

    # TOML.
    for filename in (
        "custom.toml",
        "pyproject.toml",
        "pccc.toml",
    ):
        fs.create_file(filename)
        i += 1
        with open(filename, "w") as file:
            if "pyproject.toml" in filename:
                file.write(f"[tool.pccc]\n\nbody_length = {i}\n")
            else:
                file.write(f"[pccc]\n\nbody_length = {i}\n")

    # JSON.
    for filename in (
        "package.json",
        "pccc.json",
    ):
        fs.create_file(filename)
        i += 1
        with open(filename, "w") as file:
            file.write(f'{{"pccc": {{\n  "body_length": {i}\n}}\n}}\n')

    # Not implemented.
    # YAML.
    # BespON.

    files = [
        "custom.toml",
        "pyproject.toml",
        "pccc.toml",
        "package.json",
        "pccc.json",
        # "pccc.yaml",
        # "pccc.yml",
        # "pccc.besp",
    ]

    i = 60
    for file in files:
        ccr = pccc.ConventionalCommitRunner()
        ccr.options.load(["--config", "custom.toml"])
        i += 1
        assert ccr.options.body_length == i
        fs.remove_object(file)


def test_no_config_files(fs):
    """Should use defaults if no configuration files."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load("")

    assert ccr.options.header_length == 50
    assert ccr.options.body_length == 72


def test_malformed_config_file(capsys, fs):
    """Should use defaults with malformed configuration files."""
    ccr = pccc.ConventionalCommitRunner()

    # Hot garbage.
    fn = "hot-garbage"
    fs.create_file(fn)
    with open(fn, "w") as f:
        f.write("This file is hot garbage.\n")

    ccr.options.load(["--config", fn])
    assert ccr.options.header_length == 50
    assert ccr.options.body_length == 72


def test_nonexistent_config_files():
    """Should use defaults with non-existent configuration files."""
    files = [
        "no.toml",
        "no.json",
        "no.yaml",
        "no.besp",
    ]

    for file in files:
        ccr = pccc.ConventionalCommitRunner()
        ccr.options.load(["--config", file])

        assert ccr.options.header_length == 50
        assert ccr.options.body_length == 72


def test__determine_file_format_toml(fs):
    """Should identify a TOML file."""
    filename = "config.toml"
    fs.create_file(filename)
    with open(filename, "w") as file:
        # tdata = {"pccc": str(ccr.options)}
        tdata = {
            "pccc": {
                "header_length": 50,
                "body_length": 72,
            },
        }
        toml.dump(tdata, file)

    assert pccc._determine_file_format(filename) == "toml"


def test__determine_file_format_json(fs):
    """Should identify a JSON file."""
    filename = "config.toml"
    fs.create_file(filename)
    with open(filename, "w") as file:
        data = {
            "pccc": {
                "header_length": 50,
                "body_length": 72,
            },
        }
        json.dump(data, file)

    assert pccc._determine_file_format(filename) == "json"


def test__determine_file_format_yaml(fs):
    """Should identify a YAML file."""
    filename = "config.yaml"
    fs.create_file(filename)
    with open(filename, "w") as file:
        data = {
            "pccc": {
                "header_length": 50,
                "body_length": 72,
            },
        }

        yaml = YAML(typ="safe")
        yaml.dump(data, file)

    with pytest.raises(ValueError):
        pccc._determine_file_format(filename)


def test__determine_file_format_bespon(fs):
    """Should identify a BespON file."""
    filename = "config.besp"
    fs.create_file(filename)
    with open(filename, "w") as file:
        data = {
            "pccc": {
                "header_length": 50,
                "body_length": 72,
            },
        }

        bespon.dump(data, file)

    with pytest.raises(ValueError):
        pccc._determine_file_format(filename)


def test__determine_file_format_no_file(fs):
    """Should raise ``FileNotFoundError``."""
    filename = "not.here"

    with pytest.raises(FileNotFoundError):
        pccc._determine_file_format(filename)


def test__load_toml_file(fs):
    """Should load a TOML file."""
    filename = "config.toml"
    fs.create_file(filename)
    with open(filename, "w") as file:
        data = {
            "pccc": {
                "header_length": 48,
                "body_length": 68,
            },
        }
        toml.dump(data, file)

    options = pccc._load_toml_file(filename)

    assert options["header_length"] == 48
    assert options["body_length"] == 68


def test__load_toml_file_bad_format(fs):
    """Should raise ``TomlDecodeError``."""
    filename = "config.toml"
    fs.create_file(filename)
    with open(filename, "w") as file:
        data = {
            "pccc": {
                "header_length": 48,
                "body_length": 68,
            },
        }
        json.dump(data, file)

    with pytest.raises(toml.TomlDecodeError):
        pccc._load_toml_file(filename)


def test__load_toml_file_no_file(fs):
    """Should raise ``FileNotFoundError``."""
    filename = "not.here"

    with pytest.raises(FileNotFoundError):
        pccc._load_toml_file(filename)


def test__load_json_file(fs):
    """Should load a JSON file."""
    filename = "config.json"
    fs.create_file(filename)
    with open(filename, "w") as file:
        data = {
            "pccc": {
                "header_length": 48,
                "body_length": 68,
            },
        }
        json.dump(data, file)

    options = pccc._load_json_file(filename)

    assert options["header_length"] == 48
    assert options["body_length"] == 68


def test__load_json_file_bad_format(fs):
    """Should raise ``JSONDecodeError``."""
    filename = "config.json"
    fs.create_file(filename)
    with open(filename, "w") as file:
        data = {
            "pccc": {
                "header_length": 48,
                "body_length": 68,
            },
        }
        toml.dump(data, file)

    with pytest.raises(json.JSONDecodeError):
        pccc._load_json_file(filename)


def test__load_json_file_no_file(fs):
    """Should raise ``FileNotFoundError``."""
    filename = "not.here"

    with pytest.raises(FileNotFoundError):
        pccc._load_json_file(filename)


def test__load_yaml_file():
    """Should raise ``NotImplementedError``."""
    filename = "not.here"

    with pytest.raises(NotImplementedError):
        pccc._load_yaml_file(filename)


def test__load_bespon_file():
    """Should raise ``NotImplementedError``."""
    filename = "not.here"

    with pytest.raises(NotImplementedError):
        pccc._load_bespon_file(filename)


def test_show_license_info(capsys):
    """Test ``--show-license`` and ``--show-warranty`` CLI options."""
    expected = """\
pccc:  The Python Conventional Commit Checker.

Copyright (C) 2021-2022 Jeremy A Gray <jeremy.a.gray@gmail.com>.

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
