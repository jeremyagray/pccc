"""pccc parser functions and classes."""

import copy
import fileinput
import re

import pyparsing as pp

from .config import get_configuration_options

# import textwrap  # wrap text
# import pyenchant  # spell check


class ConventionalCommit:
    """Class describing a conventional commit.

    Parses a cleaned commit message and stores the parsed information
    or parser exceptions for further use.

    Attributes
    ----------
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
    """

    def __init__(self, raw):
        """Create a ConventionalCommit.

        Create a ConventionalCommit by parsing a cleaned commit
        message string.  Parsing exceptions are caught and stored for
        further use.

        Parameters
        ----------
        raw : string
            A cleaned, unparsed commit message.

        Returns
        -------
        object
            A ConventionalCommit.
        """
        self.raw = raw
        try:
            cc = _parse_commit(raw)
            self.header = copy.deepcopy(cc["header"])
            self.body = copy.deepcopy(cc["body"])
            self.breaking = copy.deepcopy(cc["breaking"])
            self.footers = copy.deepcopy(cc["footers"])
            self.exc = None
        except pp.ParseException as exc:
            self.exc = exc
            print(exc)

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
        """Recreate a ConventionalCommit object.

        Returns
        -------
        string
            A string representation of the ConventionalCommit object.
        """
        return fr"ConventionalCommit(raw={self.raw})"


def _list_to_option_re(list):
    """Convert a list to an option regular expression string."""
    return fr"({'|'.join(list)})"


def _parse_commit(raw):
    r"""Parse a conventional commit message.

    Parse a conventional commit message according to the
    `specification
    <https://www.conventionalcommits.org/en/v1.0.0/#specification>`,
    including user defined types, scopes, and footers.

    BNF for conventional commit (v1.0.0):
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

    Parameters
    ----------
    raw : string
        A string representing the cleaned, unparsed commit message.

    Returns
    -------
    dict
        The parsed fields of the commit.
    """
    pp.ParserElement.defaultWhitespaceChars = "\t"

    types = [
        "ci",
        "docs",
        "feat",
        "fix",
        "perf",
        "refactor",
        "style",
        "test",
    ]

    scopes = [
        "foo",
        "bar",
        "baz",
        "parser",
    ]

    footers = [
        "Signed-Off-By",
    ]

    msg_obj = {
        "header": {
            "type": "",
            "scope": "",
            "description": "",
            "length": 0,
        },
        "body": {
            "paragraphs": [],
            "longest": 0,
        },
        "breaking": {
            "flag": False,
            "token": "",
            "separator": "",
            "value": "",
        },
        "footers": [
            # {
            #     "token": "",
            #     "separator": "",
            #     "value": "",
            # },
        ],
    }

    def _header_handler(s, loc, tokens):
        """Find the length of the header."""
        tokens[0].append(tokens[0].pop()[0])
        msg_obj["header"]["length"] = len("".join(tokens[0]))

    def _header_type_handler(s, loc, tokens):
        """Get the header type field."""
        msg_obj["header"]["type"] = tokens[0]

    def _header_scope_handler(s, loc, tokens):
        """Get the header scope field."""
        msg_obj["header"]["scope"] = tokens[0].lstrip("(").rstrip(")")

    def _header_desc_handler(s, loc, tokens):
        """Get the header description."""
        msg_obj["header"]["description"] = tokens[0][0].strip()

    def _breaking_flag_handler(s, loc, tokens):
        """Set the breaking flag state."""
        if tokens[0] == "!":
            msg_obj["breaking"]["flag"] = True

    def _breaking_handler(s, loc, tokens):
        """Get the breaking change field values."""
        msg_obj["breaking"]["token"] = tokens[0][0]
        msg_obj["breaking"]["separator"] = tokens[0][1]
        msg_obj["breaking"]["value"] = "\n".join(tokens[0][2])

    def _footer_handler(s, loc, tokens):
        """Build the footer dicts from field values."""
        for footer in tokens:
            msg_obj["footers"].append(
                {
                    "token": footer[0],
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
                msg_obj["body"]["paragraphs"].append("".join(par))
                par = []
            else:
                par.append(line)

            if line == "\n":
                nll = True
            else:
                nll = False

            if msg_obj["body"]["longest"] < len(line):
                msg_obj["body"]["longest"] = len(line)

    eos = pp.StringEnd()

    type = (
        pp.Regex(_list_to_option_re(types))
        .setResultsName("type", listAllMatches=True)
        .setParseAction(_header_type_handler)
    )
    scope = (
        pp.Regex(r"\(" + _list_to_option_re(scopes) + r"\)")
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
    breaking_token = pp.Regex(r"(BREAKING CHANGE|BREAKING-CHANGE)").setResultsName(
        "breaking-token", listAllMatches=True
    )
    footer_token = pp.Regex(_list_to_option_re(footers)).setResultsName(
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

    commit_msg.parseString(raw)

    return msg_obj


def clean_commit(commit):
    r"""Clean a commit before parsing.

    Remove all comment lines (matching the regular expression
    "^\\s*#.*$) from a commit message before parsing.

    Parameters
    ----------
    commit : string
        The uncleaned, unparsed commit message.

    Returns
    -------
    string
        The cleaned commit.
    """
    comment = re.compile(r"^\s*#.*$")
    cleaned = ""

    for line in commit.rstrip().split("\n"):
        # Remove comments.
        if not comment.match(line):
            cleaned += line + "\n"

    return cleaned


def get_commit(options):
    r"""Read a commit from a file or STDIN.

    Parameters
    ----------
    options : dict
        The configuration options, containing the commit message
        filename.

    Returns
    -------
    string
        The uncleaned, unparsed commit message.
    """
    commit = ""

    with fileinput.FileInput(files=(options["commit"]), mode="r") as input:
        for line in input:
            commit += line

    return commit


def main():
    """Run the default program.

    Calls get_commit() and clean_commit() on the commit message,
    passing the result to ConventionalCommit for parsing.  Exits the
    program with a 0 for success, 1 for failure.
    """
    cc = ConventionalCommit(clean_commit(get_commit(get_configuration_options())))

    if cc.exc:
        exit(1)
    else:
        exit(0)
