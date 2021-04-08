# SPDX-License-Identifier: GPL-3.0-or-later
#
# pccc, the Python Conventional Commit Checker.
# Copyright (C) 2020-2021 Jeremy A Gray <jeremy.a.gray@gmail.com>.
"""pccc exceptions."""


class NotParseableError(Exception):
    """pccc file not parseable exception."""

    def __init__(self, fn):
        """Initialize a NotParseableError() exception."""
        self.fn = fn
        self.message = f"File {fn} could not be parsed."
        super().__init__(self.message)
