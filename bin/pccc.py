#!/usr/bin/env python

import sys

sys.path.insert(0, '/home/gray/src/work/pccc')

from pccc import ConventionalCommit as CC

if __name__ == '__main__':
    msg = r"""fix(parser)!: fix parser bug

Fix big parser bug. Fix big parser bug. Fix big parser bug. Fix big
parser bug. Fix big parser bug. Fix big parser bug. Fix big parser
bug. Fix big parser bug. Fix big parser bug. Fix big parser bug. Fix
big parser bug.

Also, fix your mom.

BREAKING CHANGE: Your face.
Signed-Off-By: Jeremy A Gray <jeremy.a.gray@gmail.com>
Signed-Off-By: Your Mom <your.mom@gmail.com>
"""

    cc = CC(msg)
    # print(cc)

    if cc.exc:
        exit(1)
    else:
        exit(0)
