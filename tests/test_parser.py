#!/usr/bin/env python

import sys

sys.path.insert(0, '/home/gray/src/work/pccc')

import pccc  # noqa: E402

commit_msg = r"""fix: fix parser bug

Fix big parser bug.

Also, fix your mom.

BREAKING CHANGE: Your face.
Signed-Off-By: Jeremy A Gray <jeremy.a.gray@gmail.com>
"""

# [
# [['fix', ': ', ['fix parser bug']],
# [['Fix big parser bug.'], ['Also, fix your mom.']],
# ['BREAKING CHANGE', ': ', ['Your face.']],
# ['Signed-Off-By', ': ', ['Jeremy A Gray <jeremy.a.gray@gmail.com>']]
# ]


def test_header():
    commit_msg = r"""fix: fix parser bug
"""
    parsed = pccc.parse_commit(commit_msg)
    assert parsed[0][0] == "fix"
    assert parsed[0][1] == ": "
    assert parsed[0][2][0] == "fix parser bug"


def test_header_with_scope():
    commit_msg = r"""fix(parser): fix parser bug
"""
    parsed = pccc.parse_commit(commit_msg)
    assert parsed[0][0] == "fix"
    assert parsed[0][1] == "(parser)"
    assert parsed[0][2] == ": "
    assert parsed[0][3][0] == "fix parser bug"


def test_header_with_flag():
    commit_msg = r"""fix!: fix parser bug
"""
    parsed = pccc.parse_commit(commit_msg)
    assert parsed[0][0] == "fix"
    assert parsed[0][1] == "!"
    assert parsed[0][2] == ": "
    assert parsed[0][3][0] == "fix parser bug"
