# SPDX-License-Identifier: GPL-3.0-or-later
#
# pccc, the Python Conventional Commit Checker.
# Copyright (C) 2020-2021 Jeremy A Gray <jeremy.a.gray@gmail.com>.
"""pccc parser functions and classes."""

import copy
import fileinput

# import pyenchant  # spell check
import re
import sys
import textwrap

import pyparsing as pp

# from .config import get_configuration_options
from .config import Config


class ConventionalCommit:
    """Class describing a conventional commit.

    Data structure containg the raw commit message, cleaned commit
    message, parsed conventional commit tokens, and parser exceptions
    for further use.

    Attributes
    ----------
    raw : string
       An unprocessed commit message.
    cleaned : string
       A cleaned, unparsed commit message.
    header : dict
        Header fields and values.
    header["type"] : string
        Header type.
    header["scope"] : string
        Header scope.
    header["description"] : string
        Header description.
    header["length"] : int
        The length of the header.
    body : dict
        Body fields and values.
    body["paragraphs"] : [string]
        The paragraphs of the body.
    body["longest"] : int
        The length of the longest body line.
    breaking : dict
        Breaking change fields and values.
    breaking["flag"] : boolean
        The breaking change flag is present, or not.
    breaking["token"] : string
        A string representing the breaking change token; either
        "BREAKING CHANGE" or "BREAKING-CHANGE" (for footer
        compatibility).
    breaking["separator"] : string
        A string representing the breaking change separator; either ": "
        or " #" (supposedly).
    breaking["value"] : string
        The breaking change value (description).
    footers : [dict]
        An array of footer dicts, which are identical to the breaking
        dicts, without a "flag" field.
    exc : object
        ParseException raised during parsing, or ``None``.
    """

    def __init__(self):
        """Create a ``ConventionalCommit()``.

        Create a ``ConventionalCommit()``.

        Returns
        -------
        object
            A ``ConventionalCommit()``.
        """
        self.raw = ""
        self.cleaned = ""
        self.header = {
            "type": "",
            "scope": "",
            "description": "",
            "length": 0,
        }
        self.body = {
            "paragraphs": [],
            "longest": 0,
        }
        self.breaking = {
            "flag": False,
            "token": "",
            "separator": "",
            "value": "",
        }
        self.footers = []
        self.exc = None

    def __str__(self):
        """Stringify a parsed commit.

        Returns
        -------
        string
            A string representation of the cleaned, parsed commit.
        """
        rs = self._stringify_header()
        body = self._stringify_body()
        breaking = self._stringify_breaking()
        footers = self._stringify_footers()
        sep = "\n\n"

        if body:
            rs += sep + body
        if breaking:
            rs += sep + breaking
            sep = "\n"
        if footers:
            rs += sep + footers

        return rs + "\n"

    def _stringify_header(self):
        """Stringify a parsed commit header."""
        if self.header["scope"] != "" and not self.breaking["flag"]:
            header = (
                fr"{self.header['type']}({self.header['scope']}):"
                fr" {self.header['description']}"
            )
        elif self.header["scope"] != "" and self.breaking["flag"]:
            header = (
                fr"{self.header['type']}({self.header['scope']})!:"
                fr" {self.header['description']}"
            )
        elif self.header["scope"] == "" and not self.breaking["flag"]:
            header = fr"{self.header['type']}: {self.header['description']}"
        elif self.header["scope"] == "" and self.breaking["flag"]:
            header = fr"{self.header['type']}!: {self.header['description']}"

        return header

    def _stringify_body(self):
        """Stringify a parsed commit body."""
        if len(self.body["paragraphs"]) > 0:
            return "\n".join(self.body["paragraphs"]).rstrip()
        else:
            return ""

    def _stringify_breaking(self):
        """Stringify a parsed commit breaking change."""
        if self.breaking["value"] == "":
            return ""
        else:
            return (
                f"{self.breaking['token']}{self.breaking['separator']}"
                f"{self.breaking['value']}"
            )

    def _stringify_footers(self):
        """Stringify a parsed commit footer array."""
        footers = []

        for footer in self.footers:
            footers.append(f"{footer['token']}{footer['separator']}{footer['value']}")

        return "\n".join(footers)

    def __repr__(self):
        """Recreate a ``ConventionalCommit()``.

        Returns
        -------
        string
            A string representation of a ``ConventionalCommit()``.
        """
        return fr"ConventionalCommit(raw={self.raw})"


class ConventionalCommitRunner(ConventionalCommit):
    """``ConventionalCommit()`` subclass with methods for execution.

    A ``ConventionalCommit()`` with addtional methods for loading,
    cleaning, and parsing a raw commit message as well as an
    ``Config()`` attribute for loading and accessing configuration
    information.

    Attributes
    ----------
    options : object
        A ``Config()`` object for handling configuration.
    """

    def __init__(self):
        """Create a ``ConventionalCommitRunner()``.

        Create a ``ConventionalCommitRunner()`` and adds a
        ``Config()`` object for configuration management.

        Returns
        -------
        object
            A ``ConventionalCommitRunner()``.
        """
        # Add a Config() object.
        self.options = Config()

        super().__init__()

    def clean(self):
        r"""Clean a commit before parsing.

        Remove all comment lines (matching the regular expression
        ``"^\\s*#.*$"``) from a commit message before parsing.
        """
        comment = re.compile(r"^\s*#.*$")
        cleaned = ""

        for line in self.raw.rstrip().split("\n"):
            # Remove comments.
            if not comment.match(line):
                cleaned += line + "\n"

        self.cleaned = cleaned

    def get(self):
        r"""Read a commit from a file or ``STDIN``.

        Loads a the commit message from the file specified in the
        configuration, defaulting to ``STDIN``.
        """
        commit = ""
        try:
            with fileinput.FileInput(files=(self.options.commit), mode="r") as input:
                for line in input:
                    commit += line

            self.raw = commit
        except FileNotFoundError as error:
            print(f"{error.strerror}: {error.filename}")
            raise

    def validate_header_length(self):
        """Check that header length is correct.

        Check that header length is less than or equal to
        ``self.options.header_length``.

        Raises
        ------
        ValueError
            Indicates the commit message header exceeds its configured
            length.
        """
        if self.header["length"] > self.options.header_length:
            raise ValueError(
                f"Commit header length ({self.header['length']}) exceeds"
                f" the maximum length ({self.options.header_length})."
            )

        return True

    def validate_body_length(self):
        """Check that maximum body length is correct.

        Check that the maximum body line length is less than or equal
        to ``self.options.body_length``.

        Raises
        ------
        ValueError
            Indicates the commit message body has a line that exceeds
            its configured maximum length.
        """
        if self.body["longest"] > self.options.body_length:
            raise ValueError(
                f"Commit header length ({self.body['longest']}) exceeds"
                f" the maximum length ({self.options.body_length})."
            )

        return True

    def check_body_length(self):
        """Check that maximum body length is correct.

        Check that the maximum body line length is less than or equal
        to ``self.options.body_length``.

        Returns
        ------
        boolean
            ``True`` if the maximum body line length is less than or
            equal to ``self.options.body_length``, ``False``
            otherwise.
        """
        if self.body["longest"] > self.options.body_length:
            return False

        return True

    def validate(self):
        """Validate a commit after parsing."""
        self.validate_header_length()

    def post_process(self):
        """Process commit after parsing."""
        # if ((self.options.wrap
        #      and not self.check_body_length())
        #     or self.options.rewrap):
        #     self.wrap()
        self.wrap()

    def wrap(self):
        """Wrap a commit body to a given length."""
        self.body["paragraphs"] = list(
            map(
                lambda item: "\n".join(textwrap.wrap(item, self.options.body_length)),
                self.body["paragraphs"],
            )
        )

    def parse(self):
        r"""Parse a conventional commit message.

        Parse a conventional commit message according to the
        `specification
        <https://www.conventionalcommits.org/en/v1.0.0/#specification>`_,
        including user defined types, scopes, and footers.

        BNF for conventional commit (v1.0.0)::

            type :: ( feat | fix | 'user defined types' )
            scope :: ( '(' 'user defined scopes' ')' )
            header-breaking-flag :: !
            header-sep :: ': '
            header-desc :: .*
            header :: type scope? header-breaking-flag? header-sep header-desc
            breaking-token :: ( BREAKING CHANGE | BREAKING-CHANGE )
            footer-sep :: ( ': ' | ' #' )
            breaking-value :: .*
            breaking :: breaking-token footer-sep breaking-value
            footer-token :: ( 'user defined footers' )
            footer-value :: .*
            footer :: footer-token footer-sep footer-value
            line :: .*
            newline :: '\n'
            skip :: newline newline
            par :: ( line newline )+
            body :: skip par+
            commit-msg :: header body? breaking? footer*
        """
        pp.ParserElement.defaultWhitespaceChars = "\t"

        types = self.options.types
        scopes = self.options.scopes
        footers = self.options.footers

        def _header_handler(s, loc, tokens):
            """Find the length of the header."""
            tokens[0].append(tokens[0].pop()[0])
            self.header["length"] = len("".join(tokens[0]))

        def _header_type_handler(s, loc, tokens):
            """Get the header type field."""
            self.header["type"] = tokens[0]

        def _header_scope_handler(s, loc, tokens):
            """Get the header scope field."""
            self.header["scope"] = tokens[1]

        def _header_desc_handler(s, loc, tokens):
            """Get the header description."""
            self.header["description"] = tokens[0][0].strip()

        def _breaking_flag_handler(s, loc, tokens):
            """Set the breaking flag state."""
            if tokens[0] == "!":
                self.breaking["flag"] = True

        def _breaking_handler(s, loc, tokens):
            """Get the breaking change field values."""
            self.breaking["token"] = tokens[0][0]
            self.breaking["separator"] = tokens[0][1]
            self.breaking["value"] = "\n".join(tokens[0][2])

        def _footer_handler(s, loc, tokens):
            """Build the footer dicts from field values."""
            for footer in tokens:
                self.footers.append(
                    {
                        "token": footer[0].lower().capitalize(),
                        "separator": footer[1],
                        "value": "\n".join(tokens[0][2]),
                    }
                )

        def _body_handler(s, loc, tokens):
            """Process the body tokens.

            Calculate the longest body line and store the body paragraphs.
            """
            nll = False
            par = []
            for line in tokens:
                if nll and line == "\n":
                    self.body["paragraphs"].append("".join(par))
                    par = []
                else:
                    par.append(line)

                if line == "\n":
                    nll = True
                else:
                    nll = False

                if self.body["longest"] < len(line):
                    self.body["longest"] = len(line)

        eos = pp.StringEnd()

        type = (
            pp.oneOf(types)
            .setResultsName("type", listAllMatches=True)
            .setParseAction(_header_type_handler)
        )
        scope = (
            ("(" + pp.oneOf(scopes) + ")")
            .setResultsName("scope", listAllMatches=True)
            .setParseAction(_header_scope_handler)
        )
        header_breaking_flag = (
            pp.Regex(r"!")
            .setResultsName("header-breaking-flag", listAllMatches=True)
            .setParseAction(_breaking_flag_handler)
        )
        header_sep = pp.Regex(r": ")
        newline = pp.LineEnd().suppress()
        header_desc = (
            pp.Group(~newline + ~eos + pp.Regex(r".*"))
            .setResultsName("header-desc", listAllMatches=True)
            .setParseAction(_header_desc_handler)
        )
        header = (
            pp.Group(
                type
                + pp.Optional(scope)
                + pp.Optional(header_breaking_flag)
                + header_sep
                + header_desc
            )
            .setResultsName("header", listAllMatches=True)
            .setParseAction(_header_handler)
        )

        footer_sep = pp.Regex(r"(: | #)").setWhitespaceChars("	\n")
        breaking_token = pp.oneOf(
            ("BREAKING CHANGE", "BREAKING-CHANGE")
        ).setResultsName("breaking-token", listAllMatches=True)
        footer_token = pp.oneOf(footers, caseless=True).setResultsName(
            "footer-token", listAllMatches=True
        )

        breaking_value = (
            pp.Group(pp.OneOrMore(~eos + ~footer_token + pp.Regex(r".*")))
            .setWhitespaceChars(" 	")
            .setResultsName("breaking-value", listAllMatches=True)
        )
        breaking = (
            pp.Group(breaking_token + footer_sep + breaking_value)
            .setResultsName("breaking", listAllMatches=True)
            .setParseAction(_breaking_handler)
        )

        footer_value = (
            pp.Group(pp.OneOrMore(~eos + ~footer_token + pp.Regex(r".*")))
            .setWhitespaceChars(" 	")
            .setResultsName("footer-value", listAllMatches=True)
        )
        footer = (
            pp.Group(footer_token + footer_sep + footer_value)
            .setResultsName("footers", listAllMatches=True)
            .setParseAction(_footer_handler)
        )

        footer_types = pp.Group(breaking ^ footer)

        line = pp.Regex(r".*")
        bnewline = pp.LineEnd()
        skip = bnewline + bnewline
        par = pp.OneOrMore(~eos + ~footer_types + ~bnewline + line + bnewline)
        body = skip + pp.OneOrMore(
            ~eos + ~footer_types + par + pp.Optional(bnewline)
        ).setParseAction(_body_handler)

        commit_msg = (
            header + pp.Optional(body) + pp.Optional(breaking) + pp.ZeroOrMore(footer)
        ).setResultsName("commit-msg", listAllMatches=True)

        commit_msg.parseString(self.cleaned)

        return


def main(argv=None):
    """Run the default program.

    Creates a ``ConventionalCommitRunner()``; loads the configuration
    options; gets, cleans, and parses the commit; checks for
    exceptions; and exits the program with a 0 for success, 1 for
    failure.  Additionally, the commit message is mirrored to standard
    output unchanged on failure.
    """
    runner = ConventionalCommitRunner()
    runner.options.load(argv)
    runner.options.validate()
    runner.get()
    runner.clean()

    try:
        runner.parse()
        runner.validate_header_length()
        runner.post_process()
        sys.exit(0)
    except ValueError as error:
        print(error, file=sys.stderr)
        print(runner.raw, file=sys.stdout)
        sys.exit(1)
    except pp.ParseException as error:
        print(
            f"parse error at {error.lineno}:{error.col}: {error.line}",
            file=sys.stderr,
        )
        print(runner.raw, file=sys.stdout)
        sys.exit(1)
