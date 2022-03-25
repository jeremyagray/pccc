"""Config unit tests."""

import json
import os
import re
import shutil
import sys

import pytest
import toml
from hypothesis import example
from hypothesis import given
from hypothesis import strategies as st

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
        tdata = {"tool": {"pccc": data["pccc"]}}
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
        toml.dump({"tool": {"pccc": data["pccc"]}}, f)

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
        # repr contains correct wrap setting.
        assert re.search(fr"\s+wrap={ccr.options.wrap},\s+", actual["string"])
        # repr contains correct force_wrap setting.
        assert re.search(
            fr"\s+force_wrap={ccr.options.force_wrap},\s+", actual["string"]
        )
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
            fr",\s+footers={re.escape(repr(ccr.options.footers))},\s+",
            actual["string"],
        )
        # repr contains correct required footers list.
        assert re.search(
            r",\s+required_footers="
            fr"{re.escape(repr(ccr.options.required_footers))},\s+",
            actual["string"],
        )
        # repr contains correct format.
        assert re.search(
            fr",\s+format=\"{ccr.options.format}\"\)",
            actual["string"],
        )

        # repr ends with close parenthesis.
        assert re.search(r"\)$", actual["string"])


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
            if filename == "pyproject.toml":
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
