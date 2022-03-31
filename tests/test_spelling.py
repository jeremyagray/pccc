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
        ccr._add_spell_ignore_word(line)

        assert word in ccr.spell_ignore_words


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
def test_clean_finds_ignored_words(words):
    """Should find ignored words."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load("")
    ccr.raw = (
        "feat(parser): add closing footer\n\n"
        "Add closing foter to allow github issue closing.\n"
    )

    for word in words:
        line = f"# IGNORE:  {word}\n"
        ccr.raw += line

    ccr.clean()

    for word in words:
        assert word in ccr.spell_ignore_words


def test_spell_check_commit():
    """Should find spelling errors."""
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load("")
    ccr.options.spell_check = True
    ccr.raw = (
        "feat(parser): add closing footer\n\n"
        "Add closing foter to allow github issue closing.\n"
    )
    ccr.clean()
    ccr.parse()
    ccr.validate()
    ccr.post_process()

    assert "# ERROR:  foter" in ccr.errors
    assert "# ERROR:  github" in ccr.errors


def test_spell_check_commit_main(fs, capsys):
    """Should handle spelling error interaction."""
    # Commit message.
    fn = "./pyproject.toml"
    fs.create_file(fn)
    with open(fn, "w") as file:
        file.write(
            r"""[tool.pccc]

header_length = 50
body_length = 72
wrap = true
force_wrap = true
spell_check = true
repair = false
ignore_generated_commits = true

generated_commits = [
  '''^\(tag:\s+v\d+\.\d+\.\d\)\s+\d+\.\d+\.\d+$''',
  '''^Merge branch 'master' of.*$''',
]

types = [
  "build",
  "ci",
  "depends",
  "docs",
  "feat",
  "fix",
  "perf",
  "refactor",
  "release",
  "style",
  "test",
]

scopes = [
  "config",
  "docs",
  "parser",
  "tooling",
]

footers = [
  "github-closes",
  "signed-off-by",
]

required_footers = [
  "signed-off-by",
]
"""
        )

    # Commit message.
    fn = "./commit-msg"
    fs.create_file(fn)
    with open(fn, "w") as file:
        file.write(
            "feat(parser): add closing footer\n\n"
            "Add closing foter to allow github issue closing.\n"
        )

    with pytest.raises(SystemExit) as error:
        pccc.main([fn])

    capture = capsys.readouterr()
    assert "# ERROR:  foter" in capture.out
    assert "# IGNORE:  foter" in capture.out
    assert "# ERROR:  github" in capture.out
    assert "# IGNORE:  github" in capture.out
    assert error.type == SystemExit
    assert error.value.code == 1
