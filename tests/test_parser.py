#!/usr/bin/env python

import json
import os
import re
import sys

import pyparsing as pp
import pytest

sys.path.insert(0, "/home/gray/src/work/pccc")

from pccc import ConventionalCommit as CC  # noqa: E402


def get_good_commits():
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
    commits = []

    with os.scandir("./tests/bad") as it:
        for entry in it:
            if entry.is_file():
                commit = ""
                with open(entry.path, "r") as file:
                    for line in file:
                        commit += line
                commits.append(tuple(commit))

    return commits


@pytest.mark.parametrize(
    "obj",
    get_good_commits(),
)
def test_good_commits(obj):
    cc = CC(obj[0]["commit"])

    assert cc.header == obj[0]["header"]
    assert cc.body == obj[0]["body"]
    assert cc.breaking == obj[0]["breaking"]
    assert cc.footers == obj[0]["footers"]

    assert cc.__str__() == obj[0]["commit"]
    assert cc.__repr__() == fr"ConventionalCommit(raw={obj[0]['commit']})"


@pytest.mark.parametrize(
    "raw",
    get_bad_commits(),
)
def test_bad_commits(raw):
    raw = """fix(bob): fix parser bug\n"""
    cc = CC(raw)

    assert isinstance(cc.exc, pp.ParseException)
