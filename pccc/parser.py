# ******************************************************************************
#
# pccc, the Python Conventional Commit Checker.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2020-2022 Jeremy A Gray <gray@flyquackswim.com>.
#
# ******************************************************************************

"""pccc parser functions and classes."""

import copy
import fileinput

# import pyenchant  # spell check
import re
import sys
import textwrap

import pyparsing as pp

from .config import Config
from .exceptions import BodyLengthError
from .exceptions import BreakingLengthError
from .exceptions import ClosesIssueParseException
from .exceptions import HeaderLengthError

PYPARSING_DEBUG = False


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
    closes_issues : iterable of dict
        An array of dicts, containing the ``owner``, ``repo``, and
        ``number`` keys, if available.
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
            "longest": 0,
        }
        self.footers = []
        self.closes_issues = []
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
                rf"{self.header['type']}({self.header['scope']}):"
                rf" {self.header['description']}"
            )
        elif self.header["scope"] != "" and self.breaking["flag"]:
            header = (
                rf"{self.header['type']}({self.header['scope']})!:"
                rf" {self.header['description']}"
            )
        elif self.header["scope"] == "" and not self.breaking["flag"]:
            header = rf"{self.header['type']}: {self.header['description']}"
        elif self.header["scope"] == "" and self.breaking["flag"]:
            header = rf"{self.header['type']}!: {self.header['description']}"

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
        return rf"ConventionalCommit(raw={self.raw})"


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

        Returns
        -------
        boolean
            True, if the header length validates.

        Raises
        ------
        HeaderLengthError
            Indicates the commit message header exceeds its configured
            length.
        """
        if self.header["length"] > self.options.header_length:
            raise HeaderLengthError(
                self.header["length"],
                self.options.header_length,
                self._stringify_header(),
            )

        return True

    def validate_body_length(self):
        """Check that maximum body length is correct.

        Check that the maximum body line length is less than or equal
        to ``self.options.body_length``.

        Returns
        -------
        boolean
            True, if the body length validates.

        Raises
        ------
        BodyLengthError
            Indicates the commit message body has a line that exceeds
            its configured maximum length.
        """
        self.set_body_longest()

        if self.body["longest"] > self.options.body_length:
            raise BodyLengthError(
                self.body["longest"],
                self.options.body_length,
            )

        return True

    def validate_breaking_length(self):
        """Check that maximum breaking change length is correct.

        Check that the maximum breaking change line length is less
        than or equal to ``self.options.body_length``.

        Returns
        -------
        boolean
            True, if the breaking change length validates.

        Raises
        ------
        BodyLengthError
            Indicates the commit message breaking change has a line
            that exceeds its configured maximum length.
        """
        self.set_breaking_longest()

        if self.breaking["longest"] > self.options.body_length:
            raise BreakingLengthError(
                self.breaking["longest"],
                self.options.body_length,
            )

        return True

    def validate(self):
        """Validate a commit after parsing.

        Validate a commit on header and body lengths.  Currently,
        there is no need to validate other fields as the commit will
        not parse if these are invalid.

        Returns
        -------
        boolean
            True, if the commit validates.

        Raises
        ------
        BodyLengthError
            Indicates the commit body length did not validate.  Will
            attempt to wrap the body and revalidate if
            ``self.options.wrap`` or ``self.options.force_wrap`` is
            ``True``.
        HeaderLengthError
            Indicates the commit header length did not validate.
        """
        try:
            self.validate_header_length()
        except HeaderLengthError:
            raise

        try:
            self.validate_body_length()
        except BodyLengthError:
            if self.options.wrap or self.options.force_wrap:
                self.wrap()
                self.validate_body_length()
            else:
                raise

        try:
            self.validate_breaking_length()
        except BreakingLengthError:
            if self.options.wrap or self.options.force_wrap:
                self.wrap(part="breaking")
                self.validate_breaking_length()
            else:
                raise

        return True

    def post_process(self):
        """Process commit after parsing."""
        if self.options.force_wrap:
            self.wrap()
            self.wrap(part="breaking")

    def set_body_longest(self):
        """Calculate the length of the longest body line."""
        length = 0
        for par in self.body["paragraphs"]:
            for line in par.split("\n"):
                if len(line) > length:
                    length = len(line)

        self.body["longest"] = length
        return self

    def set_breaking_longest(self):
        """Calculate the length of the longest breaking change line."""
        length = 0
        breaking = self._stringify_breaking()

        for line in breaking.split("\n"):
            if len(line) > length:
                length = len(line)

        self.breaking["longest"] = length

        return self

    def wrap(self, part="body"):
        """Wrap a commit body to a given length."""
        if part == "body":
            self.body["paragraphs"] = list(
                map(
                    lambda item: "\n".join(
                        textwrap.wrap(
                            " ".join(item.split("\n")), self.options.body_length
                        )
                    )
                    + "\n",
                    self.body["paragraphs"],
                )
            )

            self.set_body_longest()

        elif part == "breaking":
            commit = (
                self.breaking["token"]
                + self.breaking["separator"]
                + self.breaking["value"]
            )
            commit = textwrap.fill(commit, self.options.body_length)
            if sys.version_info >= (3, 6) and sys.version_info < (3, 9):
                commit = commit[
                    len(self.breaking["token"] + self.breaking["separator"]) :
                ]
            else:
                commit = commit.removeprefix(
                    self.breaking["token"] + self.breaking["separator"],
                )
            self.breaking["value"] = commit
            self.set_breaking_longest()

        return self

    def parse(self):  # noqa: C901
        r"""Parse a conventional commit message.

        Parse a conventional commit message according to the
        `specification
        <https://www.conventionalcommits.org/en/v1.0.0/#specification>`_,
        including user defined types, scopes, and footers.

        BNF for conventional commit (v1.0.0)::

            type :: ( feat | fix | 'user defined types' )
            scope :: '(' ( 'user defined scopes' ) ')'
            header-breaking-flag :: !
            header-sep :: ': '
            header-desc :: .*
            header :: type scope? header-breaking-flag? header-sep header-desc
            footer-token :: ( 'user defined footers' | BREAKING CHANGE | BREAKING-CHANGE )
            footer-sep :: ( ': ' | ' #' )
            footer-value :: .*
            footer :: footer-token footer-sep footer-value
            line :: .*
            newline :: '\n'
            skip :: newline newline
            par :: ( line newline )+
            body :: skip par+
            commit-msg :: header body? footer*

        BNF for Github commit comment issue closing syntax::

            closes-token :: 'github-closes'
            closes-sep :: footer-sep
            owner :: [a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}
            repo :: [a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}
            number :: [0-9]+
            closes-value ::
                ( ( close[ds] | fix(ed|es) | resolve[ds] )
                  owner/repo#number )
        """
        pp.ParserElement.defaultWhitespaceChars = "\t"

        types = self.options.types
        scopes = self.options.scopes
        breakers = ("BREAKING CHANGE", "BREAKING-CHANGE")
        footers = list(self.options.footers) + list(breakers)

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

        def _closes_handler(s, loc, tokens):
            """Parse the Github issue closing footers."""
            # token = "github-closes"
            # sep = ": "
            keyword = pp.oneOf(
                (
                    "close",
                    "closed",
                    "closes",
                    "fix",
                    "fixed",
                    "fixes",
                    "resolve",
                    "resolved",
                    "resolves",
                ),
            ).setResultsName("keyword", listAllMatches=True)

            owner = pp.Regex(
                r"[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}"
            ).setResultsName("owner", listAllMatches=True)

            repo = pp.Regex(
                r"[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}"
            ).setResultsName("repo", listAllMatches=True)

            number = pp.Regex(r"#[0-9]+").setResultsName(
                "number",
                listAllMatches=True,
            )

            issue = (
                pp.Group(keyword + pp.Optional(owner + "/" + repo) + number)
                .setResultsName("issue", listAllMatches=True)
                .setDebug(flag=PYPARSING_DEBUG)
            )

            issues = pp.Group(
                issue + pp.ZeroOrMore(pp.Suppress(", ") + issue) + pp.StringEnd()
            ).setDebug(flag=PYPARSING_DEBUG)

            try:
                matches = issues.parseString(tokens[0][2][0], parseAll=True)
            except (pp.ParseException) as error:
                raise ClosesIssueParseException(
                    error.line,
                    error.args[1],
                    error.args[2],
                    tokens[0][2][0],
                )

            for match in matches[0]:
                data = {}
                for (k, v) in match.items():
                    data[k] = v[0]
                self.closes_issues.append(data)

        def _footer_handler(s, loc, tokens):
            """Build the footer dicts from field values."""
            for footer in tokens:
                if footer[0].upper() in breakers:
                    _breaking_handler(s, loc, tokens)
                    continue
                if footer[0].lower() == "github-closes":
                    _closes_handler(s, loc, tokens)
                self.footers.append(
                    {
                        "token": footer[0].lower().capitalize(),
                        "separator": footer[1],
                        "value": "\n".join(footer[2]),
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
        footer_token = pp.oneOf(footers, caseless=True).setResultsName(
            "footer-token", listAllMatches=True
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

        line = pp.Regex(r".*")
        bnewline = pp.LineEnd()
        skip = bnewline + bnewline
        par = pp.OneOrMore(~eos + ~footer + ~bnewline + line + bnewline)
        body = skip + pp.OneOrMore(
            ~eos + ~footer + par + pp.Optional(bnewline)
        ).setParseAction(_body_handler)

        commit_msg = (
            header + pp.Optional(body) + pp.ZeroOrMore(footer)
        ).setResultsName("commit-msg", listAllMatches=True)

        commit_msg.parseString(self.cleaned)

        return

    def should_ignore(self):
        """Decide whether a commit message should be ignored.

        Check if ``self.options.ignore_generated_commits`` is ``True``
        and if the commit matches one of the regular expressions in
        ``self.options.generated_commits``.

        Returns
        ------
        boolean
            ``True`` if the commit matches a generated commit pattern
            and ignoring generated commits is allowed, ``False``
            otherwise.
        """
        if self.options.ignore_generated_commits:
            for pattern in self.options.generated_commits:
                msgRE = re.compile(pattern)
                if msgRE.search(self.raw):
                    return True

        return False


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

    # Check for generated commits and maybe bail.
    if runner.should_ignore():
        sys.exit(0)

    runner.clean()

    try:
        runner.parse()
        runner.validate()
        runner.post_process()
        sys.exit(0)
    except (ValueError, ClosesIssueParseException) as error:
        print(error, file=sys.stderr)
        print(runner.raw, file=sys.stdout)
        sys.exit(1)
    except (pp.ParseException) as error:
        print(
            f"parse error at {error.lineno}:{error.col}: {error.line}",
            file=sys.stderr,
        )
        print(runner.raw, file=sys.stdout)
        sys.exit(1)
