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

CC = pccc.ConventionalCommit


def create_raw_commit_files():
    """Create raw commit files for testing commit loading."""
    test_data = []
    json_file_re = re.compile(r"\d{4}\.json$")

    with os.scandir("./tests/good") as dir:
        for entry in dir:
            if entry.is_file() and json_file_re.match(entry.name):
                with open(entry.path, "r") as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError as error:
                        print(f"JSON error in file {file}")
                        raise error

                raw_fn = re.sub(r"json$", "raw", entry.path)
                with open(raw_fn, "w") as file:
                    file.write(data["raw"])

                test_data.append(tuple([raw_fn, data["raw"]]))

    return tuple(test_data)


def get_good_commits():
    """Load good commit data for tests."""
    commits = []
    json_file_re = re.compile(r"\d{4}\.json$")

    with os.scandir("./tests/good") as it:
        for entry in it:
            if entry.is_file() and json_file_re.match(entry.name):
                commit = []
                with open(entry.path, "r") as file:
                    try:
                        commit.append(json.load(file))
                    except json.JSONDecodeError as error:
                        print(f"JSON error in file {entry.name}")
                        raise error
                commits.append(tuple(commit))

    return commits


def get_bad_commits():
    """Load bad commit data for tests."""
    commits = []

    with os.scandir("./tests/bad") as it:
        for entry in it:
            if entry.is_file():
                commit = ""
                with open(entry.path, "r") as file:
                    for line in file:
                        commit += line
                commits.append(tuple([commit]))

    return commits


@pytest.mark.parametrize(
    "fn, commit",
    create_raw_commit_files(),
)
def test_load_commits_file(fn, commit):
    """Test loading commits from files."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load_file()
    ccr.options.validate()

    ccr.options.commit = fn
    ccr.get()

    assert ccr.raw == commit


@pytest.mark.parametrize(
    "fn, commit",
    create_raw_commit_files(),
)
def test_load_commits_stdin(fn, commit, monkeypatch):
    """Test loading commits from STDIN."""
    ccr = pccc.ConventionalCommitRunner()
    monkeypatch.setattr("sys.stdin", io.StringIO(commit))
    ccr.options.load_file()
    ccr.options.validate()

    ccr.options.commit = fn
    ccr.get()

    assert ccr.raw == commit


def test_load_nonexistent_commit_file():
    """Test loading a non-existent commit file."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load_file()
    ccr.options.validate()

    ccr.options.commit = "./tests/bad/nothere.json"

    with pytest.raises(FileNotFoundError):
        ccr.get()


@pytest.mark.parametrize(
    "obj",
    get_good_commits(),
)
def test_good_commits(obj):
    """Test good commits."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load_file()
    ccr.raw = obj[0]["raw"]
    ccr.clean()
    ccr.parse()

    assert ccr.header == obj[0]["header"]
    assert ccr.body == obj[0]["body"]
    assert ccr.breaking == obj[0]["breaking"]
    assert ccr.footers == obj[0]["footers"]

    assert str(ccr) == obj[0]["parsed"]
    assert repr(ccr) == fr"ConventionalCommit(raw={ccr.raw})"


@pytest.mark.parametrize(
    "raw",
    get_bad_commits(),
)
def test_bad_commits(raw):
    """Test bad commits."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load_file()
    ccr.raw = raw[0]
    ccr.clean()
    ccr.parse()

    assert isinstance(ccr.exc, pp.ParseException)
