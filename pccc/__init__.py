# SPDX-License-Identifier: GPL-3.0-or-later
#
# pccc, the Python Conventional Commit Checker.
# Copyright (C) 2020-2021 Jeremy A Gray <jeremy.a.gray@gmail.com>.
"""Python Conventional Commit Checker.

Contains the ConventionalCommit class and all the helper functions for
loading, cleaning, and parsing a conventional commit.

For programs, the main entry point should be pccc.main().  For
scripts, pccc.ConventionalCommit() may be used directly:

Examples
--------
>>> # Program:
>>> import pccc
>>> pccc.main()

>>> # From script:
>>> import pccc
>>> ccr = pccc.ConventionalCommitRunner()
>>> # Load configuration.
>>> ccr.options.load()
>>> # Get commit.
>>> ccr.get()
>>> # Clean commit.
>>> ccr.clean()
>>> # Parse commit.
>>> ccr.parse()
"""
from .config import Config
from .parser import ConventionalCommit
from .parser import ConventionalCommitRunner
from .parser import main
