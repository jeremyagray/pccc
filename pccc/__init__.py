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
>>> options = pccc.get_configuration_options()
>>> commit = pccc.get_commit(options)
>>> commit = pccc.clean_commit(commit)
>>> cc = pccc.ConventionalCommit(commit)
"""
from .config import get_configuration_options
from .parser import ConventionalCommit
from .parser import clean_commit
from .parser import get_commit
from .parser import main
