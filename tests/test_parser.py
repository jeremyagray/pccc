#!/usr/bin/env python

import json
import os
import re
import sys

import pyparsing as pp
import pytest

sys.path.insert(0, "/home/gray/src/work/pccc")

import pccc  # noqa: E402

CC = pccc.ConventionalCommit


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
                commits.append(tuple([commit]))

    return commits


@pytest.mark.parametrize(
    "obj",
    get_good_commits(),
)
def test_good_commits(obj):
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
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load_file()
    ccr.raw = raw[0]
    ccr.clean()
    ccr.parse()

    assert isinstance(ccr.exc, pp.ParseException)
