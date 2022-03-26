# ******************************************************************************
#
# pccc, the Python Conventional Commit Checker.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2020-2022 Jeremy A Gray <gray@flyquackswim.com>.
#
# ******************************************************************************

"""pccc exception tests."""

import sys

from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, "/home/gray/src/work/pccc")

import pccc  # noqa: E402


def test_stringify_closes_issue_parse_exception():
    """Should stringify a ``pccc.ClosesIssueParseException()``."""
    begin = "begin"
    bad = "x"
    end = "end"
    string = begin + bad + end
    location = len(begin)
    message = "error"
    element = None

    error = pccc.ClosesIssueParseException(
        string,
        location,
        message,
        element,
    )

    assert str(error) == (
        "One or more malformed Github issue references on or after"
        f" character position {location + 1} in"
        f'"{begin}[{bad}]{end}".'
        f"\nparseable: {begin}"
        f"\nunparseable: {bad + end}"
    )


def test_reproduce_closes_issue_parse_exception():
    """Should reproduce a ``pccc.ClosesIssueParseException()``."""
    begin = "begin"
    bad = "x"
    end = "end"
    string = begin + bad + end
    location = len(begin)
    message = "error"
    element = None

    error = pccc.ClosesIssueParseException(
        string,
        location,
        message,
        element,
    )

    assert repr(error) == (
        "ClosesIssueParseException("
        f"string={repr(string)},"
        f" loc={repr(location)},"
        f" msg={repr(message)},"
        f" elem={repr(element)},"
        ")"
    )


@given(length=st.integers(min_value=71, max_value=100))
def test_stringify_header_length_error(length):
    """Should stringify a ``pccc.HeaderLengthError()``."""
    max = 50
    header = ("fix(this): ********************************************",)

    error = pccc.HeaderLengthError(
        length,
        max,
        header,
    )

    assert str(error) == (
        f"Commit header length ({length}) exceeds the maximum length ({max})."
    )


@given(
    length=st.integers(min_value=80, max_value=120),
    max=st.integers(min_value=70, max_value=78),
)
def test_reproduce_header_length_error(length, max):
    """Should reproduce a ``pccc.HeaderLengthError()``."""
    header = ("fix(this): ********************************************",)

    error = pccc.HeaderLengthError(
        length,
        max,
        header,
    )

    message = f"Commit header length ({length}) exceeds the maximum length ({max})."

    assert repr(error) == (
        "HeaderLengthError("
        f"length={repr(length)},"
        f" max_length={repr(max)},"
        f" header={repr(header)},"
        f" message={repr(message)},"
        ")"
    )


@given(
    length=st.integers(min_value=80, max_value=120),
    max=st.integers(min_value=70, max_value=78),
)
def test_stringify_body_length_error(length, max):
    """Should stringify a ``pccc.BodyLengthError()``."""
    error = pccc.BodyLengthError(
        length,
        max,
    )

    assert str(error) == (
        f"Commit body length ({length}) exceeds the maximum length ({max})."
    )


@given(
    length=st.integers(min_value=80, max_value=120),
    max=st.integers(min_value=70, max_value=78),
)
def test_reproduce_body_length_error(length, max):
    """Should reproduce a ``pccc.BodyLengthError()``."""
    error = pccc.BodyLengthError(
        length,
        max,
    )

    message = f"Commit body length ({length}) exceeds the maximum length ({max})."

    assert repr(error) == (
        "BodyLengthError("
        f"longest={repr(length)},"
        f" max_length={repr(max)},"
        f" message={repr(message)},"
        ")"
    )


@given(
    length=st.integers(min_value=80, max_value=120),
    max=st.integers(min_value=70, max_value=78),
)
def test_stringify_breaking_length_error(length, max):
    """Should stringify a ``pccc.BreakingLengthError()``."""
    error = pccc.BreakingLengthError(
        length,
        max,
    )

    assert str(error) == (
        f"Commit breaking change length ({length}) exceeds the maximum length ({max})."
    )


@given(
    length=st.integers(min_value=80, max_value=120),
    max=st.integers(min_value=70, max_value=78),
)
def test_reproduce_breaking_length_error(length, max):
    """Should reproduce a ``pccc.BreakingLengthError()``."""
    error = pccc.BreakingLengthError(
        length,
        max,
    )

    message = (
        f"Commit breaking change length ({length}) exceeds the maximum length ({max})."
    )

    assert repr(error) == (
        "BreakingLengthError("
        f"longest={repr(length)},"
        f" max_length={repr(max)},"
        f" message={repr(message)},"
        ")"
    )
