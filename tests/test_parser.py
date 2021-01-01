#!/usr/bin/env python

import sys

import pyparsing as pp
import pytest

sys.path.insert(0, "/home/gray/src/work/pccc")

from pccc import ConventionalCommit as CC  # noqa: E402


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("fix: fix parser bug\n", ("fix", "", False)),
        ("fix(parser): fix parser bug\n", ("fix", "parser", False)),
        ("fix!: fix parser bug\n", ("fix", "", True)),
        ("fix(parser)!: fix parser bug\n", ("fix", "parser", True)),
    ],
)
def test_header_only(raw, expected):
    cc = CC(raw)
    assert cc.header["type"] == expected[0]
    assert cc.header["scope"] == expected[1]
    assert cc.breaking["flag"] == expected[2]

    assert cc.__str__() == raw
    assert cc.__repr__() == fr"ConventionalCommit(raw={raw})"


@pytest.mark.parametrize(
    "raw",
    [
        ("redo: fix parser bug\n"),
        ("redo(parser): fix parser bug\n"),
        ("redo(docs): fix parser bug\n"),
        ("fix(docs): fix parser bug\n"),
        ("fix?: fix parser bug\n"),
        ("redo!: fix parser bug\n"),
        ("fix!(parser): fix parser bug\n"),
        ("fix?(parser): fix parser bug\n"),
    ],
)
def test_bad_header_only(raw):
    raw = """fix(bob): fix parser bug\n"""
    cc = CC(raw)

    assert isinstance(cc.exc, pp.ParseException)


@pytest.mark.parametrize(
    "obj",
    [
        (
            {
                "raw": r"""fix: fix parser bug

BREAKING CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": False,
                    "token": "BREAKING CHANGE",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix(parser): fix parser bug

BREAKING CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "parser",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": False,
                    "token": "BREAKING CHANGE",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix!: fix parser bug

BREAKING CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": True,
                    "token": "BREAKING CHANGE",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix(parser)!: fix parser bug

BREAKING CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "parser",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": True,
                    "token": "BREAKING CHANGE",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix: fix parser bug

BREAKING-CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": False,
                    "token": "BREAKING-CHANGE",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix(parser): fix parser bug

BREAKING-CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "parser",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": False,
                    "token": "BREAKING-CHANGE",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix!: fix parser bug

BREAKING-CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": True,
                    "token": "BREAKING-CHANGE",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix(parser)!: fix parser bug

BREAKING-CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "parser",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": True,
                    "token": "BREAKING-CHANGE",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix: fix parser bug

BREAKING CHANGE #This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": False,
                    "token": "BREAKING CHANGE",
                    "separator": " #",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix(parser): fix parser bug

BREAKING CHANGE #This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "parser",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": False,
                    "token": "BREAKING CHANGE",
                    "separator": " #",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix!: fix parser bug

BREAKING CHANGE #This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": True,
                    "token": "BREAKING CHANGE",
                    "separator": " #",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix(parser)!: fix parser bug

BREAKING CHANGE #This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "parser",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": True,
                    "token": "BREAKING CHANGE",
                    "separator": " #",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix: fix parser bug

BREAKING-CHANGE #This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": False,
                    "token": "BREAKING-CHANGE",
                    "separator": " #",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix(parser): fix parser bug

BREAKING-CHANGE #This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "parser",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": False,
                    "token": "BREAKING-CHANGE",
                    "separator": " #",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix!: fix parser bug

BREAKING-CHANGE #This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": True,
                    "token": "BREAKING-CHANGE",
                    "separator": " #",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "raw": r"""fix(parser)!: fix parser bug

BREAKING-CHANGE #This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "parser",
                    "description": "fix parser bug",
                },
                "breaking": {
                    "flag": True,
                    "token": "BREAKING-CHANGE",
                    "separator": " #",
                    "value": "This breaks the old grammar.",
                },
            },
        ),
    ],
)
def test_header_breaking(obj):
    cc = CC(obj[0]["raw"])

    assert cc.header["type"] == obj[0]["header"]["type"]
    assert cc.header["scope"] == obj[0]["header"]["scope"]
    assert cc.header["description"] == obj[0]["header"]["description"]

    assert cc.breaking["flag"] is obj[0]["breaking"]["flag"]
    assert cc.breaking["token"] == obj[0]["breaking"]["token"]
    assert cc.breaking["value"] == obj[0]["breaking"]["value"]

    assert cc.__str__() == obj[0]["raw"]
    assert cc.__repr__() == fr"ConventionalCommit(raw={obj[0]['raw']})"


def test_commit():
    raw = r"""fix(parser)!: fix parser bug

Fix big parser bug. Fix big parser bug. Fix big parser bug. Fix big
parser bug. Fix big parser bug. Fix big parser bug. Fix big parser
bug. Fix big parser bug. Fix big parser bug. Fix big parser bug. Fix
big parser bug.

Also, format your code with black or black, whichever you prefer.

BREAKING CHANGE: This breaks the old grammar.
Signed-Off-By: Jeremy A Gray <jeremy.a.gray@gmail.com>
Signed-Off-By: John Doe <jdoe@example.com>
"""

    cc = CC(raw)

    assert cc.header["type"] == "fix"
    assert cc.header["scope"] == "parser"
    assert cc.header["description"] == "fix parser bug"

    assert (
        cc.body["paragraphs"][0]
        == r"""Fix big parser bug. Fix big parser bug. Fix big parser bug. Fix big
parser bug. Fix big parser bug. Fix big parser bug. Fix big parser
bug. Fix big parser bug. Fix big parser bug. Fix big parser bug. Fix
big parser bug.
"""
    )
    assert (
        cc.body["paragraphs"][1]
        == r"""Also, format your code with black or black, whichever you prefer.
"""
    )

    assert cc.breaking["token"] == "BREAKING CHANGE"
    assert cc.breaking["value"] == "This breaks the old grammar."
    assert cc.breaking["flag"] is True

    assert cc.footers[0]["token"] == "Signed-Off-By"
    assert cc.footers[0]["separator"] == ": "
    assert cc.footers[0]["value"] == "Jeremy A Gray <jeremy.a.gray@gmail.com>"
    assert cc.footers[1]["token"] == "Signed-Off-By"
    assert cc.footers[1]["separator"] == ": "
    assert cc.footers[1]["value"] == "John Doe <jdoe@example.com>"

    assert cc.__str__() == raw
    assert cc.__repr__() == fr"ConventionalCommit(raw={raw})"
