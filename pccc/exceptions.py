# ******************************************************************************
#
# pccc, the Python Conventional Commit Checker.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2020-2022 Jeremy A Gray <gray@flyquackswim.com>.
#
# ******************************************************************************

"""pccc exceptions."""

from pyparsing import ParseFatalException


class NotParseableError(Exception):
    """pccc file not parseable exception."""

    def __init__(self, fn):
        """Initialize a NotParseableError() exception."""
        self.fn = fn
        self.message = f"File {fn} could not be parsed."
        super().__init__(self.message)


class ClosesIssueParseException(ParseFatalException):
    """Github closes issue string not parseable."""

    def __init__(self, s, loc, message, string):
        """Initialize a ``ClosesIssueParseException``."""
        super().__init__(s, loc, message)
        self.string = string

    def __str__(self):
        """Stringify a ``ClosesIssueParseException``."""
        parseable = self.string[: self.loc]
        bad_char = self.string[self.loc]
        unparseable = self.string[self.loc + 1 :]
        msg = (
            "One or more malformed Github issue references on or after"
            f" character position {self.loc + 1} in"
            f'"{parseable}[{bad_char}]{unparseable}".'
        )
        msg += f"\nparseable: {parseable}"
        msg += f"\nunparseable: {bad_char + unparseable}"

        return msg

    def __repr__(self):
        """Reproduce a ``ClosesIssueParseException``."""
        return (
            "ClosesIssueParseException("
            f"s={repr(self.s)},"
            f" loc={repr(self.loc)},"
            f" message={repr(self.message)},"
            f" string={repr(self.string)},"
            ")"
        )
