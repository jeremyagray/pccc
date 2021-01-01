#!/usr/bin/env python

import copy

import pyparsing as pp

# import textwrap  # wrap text
# import pyenchant  # spell check
# import toml  # config files


class ConventionalCommit:
    def __init__(self, raw):
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
        if len(self.body["paragraphs"]) > 0:
            return "\n".join(self.body["paragraphs"]).rstrip()
        else:
            return ""

    def _stringify_breaking(self):
        if self.breaking["value"] == "":
            return ""
        else:
            return (
                f"{self.breaking['token']}{self.breaking['separator']}"
                f"{self.breaking['value']}"
            )

    def _stringify_footers(self):
        footers = []

        for footer in self.footers:
            footers.append(f"{footer['token']}{footer['separator']}{footer['value']}")

        return "\n".join(footers)

    def __repr__(self):
        return fr"ConventionalCommit(raw={self.raw})"


def _list_to_option_re(list):
    return fr"({'|'.join(list)})"


def _parse_commit(raw):
    """Parse a conventional commit message.

    Parse a conventional commit message according to the
    specification, including user defined types, scopes, and footers.

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
        tokens[0].append(tokens[0].pop()[0])
        msg_obj["header"]["length"] = len("".join(tokens[0]))

    def _header_type_handler(s, loc, tokens):
        msg_obj["header"]["type"] = tokens[0]

    def _header_scope_handler(s, loc, tokens):
        msg_obj["header"]["scope"] = tokens[0].lstrip("(").rstrip(")")

    def _header_desc_handler(s, loc, tokens):
        msg_obj["header"]["description"] = tokens[0][0].strip()

    def _breaking_flag_handler(s, loc, tokens):
        if tokens[0] == "!":
            msg_obj["breaking"]["flag"] = True

    def _breaking_handler(s, loc, tokens):
        msg_obj["breaking"]["token"] = tokens[0][0]
        msg_obj["breaking"]["separator"] = tokens[0][1]
        msg_obj["breaking"]["value"] = tokens[0][2][0].strip()

    def _footer_handler(s, loc, tokens):
        for footer in tokens:
            msg_obj["footers"].append(
                {
                    "token": footer[0],
                    "separator": footer[1],
                    "value": footer[2][0].strip(),
                }
            )

    def _body_handler(s, loc, tokens):
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
    breaking_value = pp.Group(~newline + ~eos + pp.Regex(r".*")).setResultsName(
        "breaking-value", listAllMatches=True
    )
    breaking = (
        pp.Group(breaking_token + footer_sep + breaking_value)
        .setResultsName("breaking", listAllMatches=True)
        .setParseAction(_breaking_handler)
    )

    footer_token = pp.Regex(_list_to_option_re(footers)).setResultsName(
        "footer-token", listAllMatches=True
    )
    footer_value = pp.Group(~newline + ~eos + pp.Regex(r".*")).setResultsName(
        "footer-value", listAllMatches=True
    )
    footer = (
        pp.Group(footer_token + footer_sep + footer_value)
        .setResultsName("footers", listAllMatches=True)
        .setParseAction(_footer_handler)
    )

    footers = pp.Group(breaking ^ footer)

    line = pp.Regex(r".*")
    bnewline = pp.LineEnd()
    skip = bnewline + bnewline
    par = pp.OneOrMore(~eos + ~footers + ~bnewline + line + bnewline)
    body = skip + pp.OneOrMore(
        ~eos + ~footers + par + pp.Optional(bnewline)
    ).setParseAction(_body_handler)

    commit_msg = (
        header + pp.Optional(body) + pp.Optional(breaking) + pp.ZeroOrMore(footer)
    ).setResultsName("commit-msg", listAllMatches=True)

    commit_msg.parseString(raw)

    return msg_obj
