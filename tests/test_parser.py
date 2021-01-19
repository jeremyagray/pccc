#!/usr/bin/env python
"""Parser unit tests."""

import io
import json
import os
import re
import sys

import pyparsing as pp
import pytest

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
                data.append(tuple(datum))

    return data


@pytest.mark.parametrize(
    "obj",
    get_commits(),
)
def test_commits(obj):
    """Test commits."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load("")
    ccr.raw = obj[0]["raw"]
    ccr.clean()

    if obj[0]["parseable"]:
        ccr.parse()

        assert ccr.header == obj[0]["header"]
        assert ccr.body == obj[0]["body"]
        assert ccr.breaking == obj[0]["breaking"]
        assert ccr.footers == obj[0]["footers"]

        assert str(ccr) == obj[0]["parsed"]
        assert repr(ccr) == fr"ConventionalCommit(raw={ccr.raw})"

        # Check header length.
        if obj[0]["header"]["length"] > 50:
            with pytest.raises(ValueError):
                ccr.check_header_length()
        else:
            assert ccr.check_header_length() is True

        # Check body length.
        if obj[0]["body"]["longest"] > 72:
            with pytest.raises(ValueError):
                ccr.check_body_length()
        else:
            assert ccr.check_body_length() is True

    else:
        with pytest.raises(pp.ParseException):
            ccr.parse()


@pytest.mark.parametrize(
    "obj",
    get_commits(),
)
def test_main_file(obj, fs):
    """Test pccc.main() with commits from files."""
    fn = "./commit-msg"
    fs.create_file(fn)
    with open(fn, "w") as file:
        file.write(obj[0]["raw"])

    if obj[0]["parseable"]:
        if not ("header_length" in obj[0]["errors"]):
            with pytest.raises(SystemExit) as error:
                pccc.main([fn])
                assert error.code == 0
        else:
            with pytest.raises(SystemExit) as error:
                pccc.main([fn])
                assert error.code == 1
    else:
        with pytest.raises(SystemExit) as error:
            pccc.main([fn])
            assert error.code == 1


@pytest.mark.parametrize(
    "obj",
    get_commits(),
)
def test_main_stdin(obj, monkeypatch):
    """Test pccc.main() with commits from STDIN."""
    monkeypatch.setattr("sys.stdin", io.StringIO(obj[0]["raw"]))

    if obj[0]["parseable"]:
        if not ("header_length" in obj[0]["errors"]):
            with pytest.raises(SystemExit) as error:
                pccc.main()
                assert error.code == 0
        else:
            with pytest.raises(SystemExit) as error:
                pccc.main()
                assert error.code == 1
    else:
        with pytest.raises(SystemExit) as error:
            pccc.main()
            assert error.code == 1


def test_load_nonexistent_commit_file():
    """Test loading a non-existent commit file."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load("")
    ccr.options.validate()

    ccr.options.commit = "./tests/parser/nothere.json"

    with pytest.raises(FileNotFoundError):
        ccr.get()
