#!/usr/bin/env python

import sys

sys.path.insert(0, '/home/gray/src/work/pccc')

import pccc

if __name__ == '__main__':
    commit_msg = r"""fix: fix parser bug

Fix big parser bug.

Also, fix your mom.

BREAKING CHANGE: Your face.
Signed-Off-By: Jeremy A Gray <jeremy.a.gray@gmail.com>
"""
    commit_msg = r"""fix(parser): fix parser bug
"""

    print(pccc.parse_commit(commit_msg))
