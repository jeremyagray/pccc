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

    def __init__(self, string, loc, msg=None, elem=None):
        """Initialize a ``ClosesIssueParseException``."""
        super().__init__(string, loc, msg=msg, elem=elem)
        self.string = string
        self.loc = loc
        self.msg = msg
        self.elem = elem

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
            f"string={repr(self.string)},"
            f" loc={repr(self.loc)},"
            f" msg={repr(self.msg)},"
            f" elem={repr(self.elem)},"
            ")"
        )


class HeaderLengthError(ValueError):
    """Header length error."""

    def __init__(self, length, max_length, header):
        """Initialize a ``HeaderLengthError``."""
        message = (
            f"Commit header length ({length}) exceeds"
            f" the maximum length ({max_length})."
        )

        super().__init__(message)
        self.length = length
        self.max_length = max_length
        self.header = header
        self.message = message

    def __str__(self):
        """Stringify a ``HeaderLengthError``."""
        return self.message

    def __repr__(self):
        """Reproduce a ``HeaderLengthError``."""
        return (
            "HeaderLengthError("
            f"length={repr(self.length)},"
            f" max_length={repr(self.max_length)},"
            f" header={repr(self.header)},"
            f" message={repr(self.message)},"
            ")"
        )


class BodyLengthError(ValueError):
    """Body length error."""

    def __init__(self, longest, max_length):
        """Initialize a ``BodyLengthError``."""
        message = (
            f"Commit body length ({longest}) exceeds"
            f" the maximum length ({max_length})."
        )

        super().__init__(message)
        self.longest = longest
        self.max_length = max_length
        self.message = message

    def __str__(self):
        """Stringify a ``BodyLengthError``."""
        return self.message

    def __repr__(self):
        """Reproduce a ``BodyLengthError``."""
        return (
            "BodyLengthError("
            f"longest={repr(self.longest)},"
            f" max_length={repr(self.max_length)},"
            f" message={repr(self.message)},"
            ")"
        )


class BreakingLengthError(ValueError):
    """Breaking change description length error."""

    def __init__(self, longest, max_length):
        """Initialize a ``BreakingLengthError``."""
        message = (
            f"Commit breaking change length ({longest}) exceeds"
            f" the maximum length ({max_length})."
        )

        super().__init__(message)
        self.longest = longest
        self.max_length = max_length
        self.message = message

    def __str__(self):
        """Stringify a ``BreakingLengthError``."""
        return self.message

    def __repr__(self):
        """Reproduce a ``BreakingLengthError``."""
        return (
            "BreakingLengthError("
            f"longest={repr(self.longest)},"
            f" max_length={repr(self.max_length)},"
            f" message={repr(self.message)},"
            ")"
        )
