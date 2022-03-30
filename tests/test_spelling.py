# ******************************************************************************
#
# pccc, the Python Conventional Commit Checker.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2020-2022 Jeremy A Gray <gray@flyquackswim.com>.
#
# ******************************************************************************

"""pccc parser spell checking tests."""

import io
import json
import os
import random
import re
import sys

import pyparsing as pp
import pytest
from hypothesis import example
from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, "/home/gray/src/work/pccc")

import pccc  # noqa: E402


@given(
    words=st.lists(
        st.text(
            min_size=1,
            alphabet=st.characters(
                whitelist_categories=(
                    "Lu",
                    "Ll",
                )
            ),
        ),
    ),
)
def test__add_spell_ignore_word(words):
    """Should add ignored words."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load("")

    for word in words:
        line = f"# IGNORE:  {word}"
        print(line)
        ccr._add_spell_ignore_word(line)

        assert word in ccr.spell_ignore_words
