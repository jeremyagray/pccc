#!/usr/bin/env python

import sys

sys.path.insert(0, '/home/gray/src/work/pccc')

from pccc import ConventionalCommit as CC  # noqa: E402

def test_header():
    msg = """fix: fix parser bug\n"""
    cc = CC(msg)

    assert cc.header["type"] == "fix"
    assert cc.header["scope"] == ""
    assert cc.header["msg"] == "fix parser bug"


def test_header_with_scope():
    msg = """fix(parser): fix parser bug\n"""
    cc = CC(msg)

    assert cc.header["type"] == "fix"
    assert cc.header["scope"] == "parser"
    assert cc.header["msg"] == "fix parser bug"


def test_header_with_flag():
    msg = """fix!: fix parser bug\n"""
    cc = CC(msg)

    assert cc.header["type"] == "fix"
    assert cc.header["scope"] == ""
    assert cc.header["msg"] == "fix parser bug"
    assert cc.breaking["flag"] is True
