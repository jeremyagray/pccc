#!/usr/bin/env python

import sys

import pyparsing as pp
import pytest

sys.path.insert(0, "/home/gray/src/work/pccc")

from pccc import ConventionalCommit as CC  # noqa: E402


@pytest.mark.parametrize(
    "msg, expected",
    [
        ("fix: fix parser bug\n", ("fix", "", False)),
        ("fix(parser): fix parser bug\n", ("fix", "parser", False)),
        ("fix!: fix parser bug\n", ("fix", "", True)),
        ("fix(parser)!: fix parser bug\n", ("fix", "parser", True)),
    ],
)
def test_header_only(msg, expected):
    cc = CC(msg)
    assert cc.header["type"] == expected[0]
    assert cc.header["scope"] == expected[1]
    assert cc.breaking["flag"] == expected[2]

    assert cc.__str__() == msg
    assert cc.__repr__() == fr"ConventionalCommit(msg={msg})"


@pytest.mark.parametrize(
    "msg",
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
def test_bad_header_only(msg):
    msg = """fix(bob): fix parser bug\n"""
    cc = CC(msg)

    assert isinstance(cc.exc, pp.ParseException)


@pytest.mark.parametrize(
    "obj",
    [
        (
            {
                "msg": r"""fix: fix parser bug

BREAKING CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "",
                    "msg": "fix parser bug",
                },
                "breaking": {
                    "flag": False,
                    "label": "BREAKING CHANGE",
                    "msg": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "msg": r"""fix(parser): fix parser bug

BREAKING CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "parser",
                    "msg": "fix parser bug",
                },
                "breaking": {
                    "flag": False,
                    "label": "BREAKING CHANGE",
                    "msg": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "msg": r"""fix!: fix parser bug

BREAKING CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "",
                    "msg": "fix parser bug",
                },
                "breaking": {
                    "flag": True,
                    "label": "BREAKING CHANGE",
                    "msg": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "msg": r"""fix(parser)!: fix parser bug

BREAKING CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "parser",
                    "msg": "fix parser bug",
                },
                "breaking": {
                    "flag": True,
                    "label": "BREAKING CHANGE",
                    "msg": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "msg": r"""fix: fix parser bug

BREAKING-CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "",
                    "msg": "fix parser bug",
                },
                "breaking": {
                    "flag": False,
                    "label": "BREAKING-CHANGE",
                    "msg": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "msg": r"""fix(parser): fix parser bug

BREAKING-CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "parser",
                    "msg": "fix parser bug",
                },
                "breaking": {
                    "flag": False,
                    "label": "BREAKING-CHANGE",
                    "msg": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "msg": r"""fix!: fix parser bug

BREAKING-CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "",
                    "msg": "fix parser bug",
                },
                "breaking": {
                    "flag": True,
                    "label": "BREAKING-CHANGE",
                    "msg": "This breaks the old grammar.",
                },
            },
        ),
        (
            {
                "msg": r"""fix(parser)!: fix parser bug

BREAKING-CHANGE: This breaks the old grammar.
""",
                "header": {
                    "type": "fix",
                    "scope": "parser",
                    "msg": "fix parser bug",
                },
                "breaking": {
                    "flag": True,
                    "label": "BREAKING-CHANGE",
                    "msg": "This breaks the old grammar.",
                },
            },
        ),
    ],
)
def test_header_breaking(obj):
    cc = CC(obj[0]["msg"])

    assert cc.header["type"] == obj[0]["header"]["type"]
    assert cc.header["scope"] == obj[0]["header"]["scope"]
    assert cc.header["msg"] == obj[0]["header"]["msg"]

    assert cc.breaking["flag"] is obj[0]["breaking"]["flag"]
    assert cc.breaking["label"] == obj[0]["breaking"]["label"]
    assert cc.breaking["msg"] == obj[0]["breaking"]["msg"]

    assert cc.__str__() == obj[0]["msg"]
    assert cc.__repr__() == fr"ConventionalCommit(msg={obj[0]['msg']})"


def test_commit():
    msg = r"""fix(parser)!: fix parser bug

Fix big parser bug. Fix big parser bug. Fix big parser bug. Fix big
parser bug. Fix big parser bug. Fix big parser bug. Fix big parser
bug. Fix big parser bug. Fix big parser bug. Fix big parser bug. Fix
big parser bug.

Also, format your code with black or black, whichever you prefer.

BREAKING CHANGE: This breaks the old grammar.
Signed-Off-By: Jeremy A Gray <jeremy.a.gray@gmail.com>
Signed-Off-By: John Doe <jdoe@example.com>
"""

    cc = CC(msg)

    assert cc.header["type"] == "fix"
    assert cc.header["scope"] == "parser"
    assert cc.header["msg"] == "fix parser bug"

    assert (
        cc.body[0]
        == r"""Fix big parser bug. Fix big parser bug. Fix big parser bug. Fix big
parser bug. Fix big parser bug. Fix big parser bug. Fix big parser
bug. Fix big parser bug. Fix big parser bug. Fix big parser bug. Fix
big parser bug.
"""
    )
    assert (
        cc.body[1]
        == r"""Also, format your code with black or black, whichever you prefer.
"""
    )

    assert cc.breaking["label"] == "BREAKING CHANGE"
    assert cc.breaking["msg"] == "This breaks the old grammar."
    assert cc.breaking["flag"] is True

    assert cc.footers[0]["label"] == "Signed-Off-By"
    assert cc.footers[0]["msg"] == "Jeremy A Gray <jeremy.a.gray@gmail.com>"
    assert cc.footers[1]["label"] == "Signed-Off-By"
    assert cc.footers[1]["msg"] == "John Doe <jdoe@example.com>"

    assert cc.__str__() == msg
    assert cc.__repr__() == fr"ConventionalCommit(msg={msg})"
