# ******************************************************************************
#
# pccc, the Python Conventional Commit Checker.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2020-2023 Jeremy A Gray <gray@flyquackswim.com>.
#
# ******************************************************************************

"""pccc parser tests."""

import io
import json
import os
import random
import re
import sys

import pyparsing as pp
import pytest
from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, "/home/gray/src/work/pccc")

import pccc  # noqa: E402


def get_commits():
    """Load commit data for tests."""
    data = []
    json_file_re = re.compile(r"\d{4}\.json$")

    with os.scandir("./tests/parser") as dir:
        for entry in dir:
            if entry.is_file() and json_file_re.match(entry.name):
                datum = []
                with open(entry.path, "r") as file:
                    try:
                        datum.append(json.load(file))
                    except json.JSONDecodeError as error:
                        print(f"JSON error in file {entry.name}")
                        raise error
                datum[0]["filename"] = entry.name
                data.append(tuple([entry.path, datum]))

    return data


@pytest.fixture
def config():
    """Load configuration file."""
    fn = "./pyproject.toml"
    with open(fn, "r") as f:
        conf_data = f.read()

    return conf_data


@st.composite
def commit(draw):
    """Generate a commit object strategy."""
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

    conf = pccc.Config(
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
                min_size=2,
                max_size=8,
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
                min_size=3,
                max_size=8,
            )
        ),
        footers=footers,
        required_footers=footers,
    )

    commit = pccc.ConventionalCommitRunner()
    commit.options = conf
    type = random.choice(commit.options.types)
    scope = random.choice(commit.options.scopes)
    description = draw(
        st.text(
            st.characters(
                whitelist_categories=("L", "N"),
                blacklist_categories=("C"),
            ),
            min_size=20,
            max_size=50 - (len(type) + len(scope) + 4),
        )
    )
    message = draw(
        st.text(
            st.characters(
                whitelist_categories=("L", "N"),
                blacklist_categories=("C"),
            ),
            min_size=50,
            max_size=500,
        )
    )

    commit.raw = f"""{type}({scope}): {description}

    {message}
    """

    return commit


@given(commit=commit())
def test_generated_commit(commit):
    """Should do something."""
    commit.clean()
    commit.parse()

    header = commit.raw.split("\n")[0]
    (type, scope) = header.split(":")[0].split("(")
    scope = scope.split(")")[0]
    print(f"type: {type} {commit.header['type']}")
    print(f"scope: {scope} {commit.header['scope']}")

    assert type == commit.header["type"]
    assert scope == commit.header["scope"]


@pytest.mark.parametrize(
    "fn, obj",
    get_commits(),
)
def test_commits(fn, obj):
    """Test commits."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load("")
    ccr.raw = obj[0]["raw"]
    ccr.clean()

    if obj[0]["parseable"]:
        ccr.parse()

        assert ccr.header == obj[0]["header"]
        # assert ccr.breaking == obj[0]["breaking"]
        assert ccr.footers == obj[0]["footers"]

        assert str(ccr) == obj[0]["parsed"]
        assert repr(ccr) == rf"ConventionalCommit(raw={ccr.raw})"

        # Check closes issues.
        if "closes_issues" in obj[0]:
            assert ccr.closes_issues == obj[0]["closes_issues"]

        # Check header length.
        if obj[0]["header"]["length"] > 50:
            with pytest.raises(ValueError):
                ccr.validate_header_length()
        else:
            assert ccr.validate_header_length() is True

        # Check body.
        ccr.options.wrap = False
        ccr.options.force_wrap = False
        if obj[0]["body"]["longest"] > 72 and obj[0]["breaking"]["longest"] > 72:
            with pytest.raises(pccc.BodyLengthError):
                ccr.validate()
        elif obj[0]["body"]["longest"] > 72 and obj[0]["breaking"]["longest"] <= 72:
            with pytest.raises(pccc.BodyLengthError):
                ccr.validate()
        elif obj[0]["body"]["longest"] <= 72 and obj[0]["breaking"]["longest"] > 72:
            with pytest.raises(pccc.BreakingLengthError):
                ccr.validate()
        else:
            assert ccr.validate_body_length() is True
            assert ccr.validate_breaking_length() is True
            assert ccr.breaking == obj[0]["breaking"]
            assert ccr.body == obj[0]["body"]

        ccr.options.wrap = True
        for length in (72, 70):
            if str(length) in obj[0]:
                ccr.options.body_length = length
                assert ccr.validate() is True
                assert ccr.body == obj[0][str(length)]["body"]
                print(length)
                print(ccr.breaking)
                print(obj[0][str(length)]["breaking"])
                assert ccr.breaking == obj[0][str(length)]["breaking"]

        ccr.options.force_wrap = True
        for length in (72, 70):
            if str(length) in obj[0]:
                ccr.options.body_length = length
                assert ccr.validate() is True
                ccr.post_process()
                assert ccr.body == obj[0][str(length)]["body"]
                assert ccr.breaking == obj[0][str(length)]["breaking"]

        for length in (70, 72):
            if str(length) in obj[0]:
                ccr.options.body_length = length
                assert ccr.validate() is True
                ccr.post_process()
                assert ccr.body == obj[0][str(length)]["body"]
                assert ccr.breaking == obj[0][str(length)]["breaking"]

    else:
        with pytest.raises(pp.ParseBaseException):
            ccr.parse()


@pytest.mark.parametrize(
    "fn, obj",
    get_commits(),
)
def test_main_file(config, fn, obj, fs, capsys):
    """Test pccc.main() with commits from files."""
    # Commit message.
    fn = "./pyproject.toml"
    fs.create_file(fn)
    with open(fn, "w") as file:
        file.write(config)

    # Commit message.
    fn = "./commit-msg"
    fs.create_file(fn)
    with open(fn, "w") as file:
        file.write(obj[0]["raw"])

    if obj[0]["parseable"]:
        if not ("header_length" in obj[0]["errors"]):
            with pytest.raises(SystemExit) as error:
                pccc.main([fn])
            capture = capsys.readouterr()
            assert capture.out == ""
            assert error.type == SystemExit
            assert error.value.code == 0
        else:
            with pytest.raises(SystemExit) as error:
                pccc.main([fn])
            capture = capsys.readouterr()
            assert capture.out[:-1] == obj[0]["raw"]
            assert error.type == SystemExit
            assert error.value.code == 1
    else:
        if "generated" in obj[0] and obj[0]["generated"]:
            obj[0]["generated"]
            with pytest.raises(SystemExit) as error:
                pccc.main([fn])
            assert error.type == SystemExit
            assert error.value.code == 0
        else:
            with pytest.raises(SystemExit) as error:
                pccc.main([fn])
            capture = capsys.readouterr()
            assert capture.out[:-1] == obj[0]["raw"]
            assert error.type == SystemExit
            assert error.value.code == 1


@pytest.mark.parametrize(
    "fn, obj",
    get_commits(),
)
def test_main_stdin(config, fn, obj, monkeypatch, fs):
    """Test pccc.main() with commits from STDIN."""
    # Configuration file.
    fn = "./pyproject.toml"
    fs.create_file(fn)
    with open(fn, "w") as file:
        file.write(config)

    monkeypatch.setattr("sys.stdin", io.StringIO(obj[0]["raw"]))

    if obj[0]["parseable"]:
        if not ("header_length" in obj[0]["errors"]):
            with pytest.raises(SystemExit) as error:
                pccc.main([])
            assert error.type == SystemExit
            assert error.value.code == 0
        else:
            with pytest.raises(SystemExit) as error:
                pccc.main([])
            assert error.type == SystemExit
            assert error.value.code == 1
    else:
        try:
            obj[0]["generated"]
            with pytest.raises(SystemExit) as error:
                pccc.main([])
            assert error.type == SystemExit
            assert error.value.code == 0
        except KeyError:
            with pytest.raises(SystemExit) as error:
                pccc.main([])
            assert error.type == SystemExit
            assert error.value.code == 1


def test_load_nonexistent_commit_file():
    """Test loading a non-existent commit file."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load("")
    ccr.options.validate()

    ccr.options.commit = "./tests/parser/nothere.json"

    with pytest.raises(FileNotFoundError):
        ccr.get()
