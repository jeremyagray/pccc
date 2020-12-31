#!/usr/bin/env python

import copy
import pyparsing as pp
# import textwrap  # wrap text
# import pyenchant  # spell check
# import toml  # config files


class ConventionalCommit():
    def __init__(self, msg):
        self.raw = msg
        try:
            msg = _parse_commit(msg)
            self.header = copy.deepcopy(msg['header'])
            self.body = copy.deepcopy(msg['body']['paragraphs'])
            self.breaking = copy.deepcopy(msg['breaking'])
            self.footers = copy.deepcopy(msg['footers'])
            self.exc = None
        except pp.ParseException as exc:
            self.exc = exc
            print(exc)

    def __str__(self):
        parts = []
        parts.append(self._stringify_header())
        parts.append(self._stringify_body())
        parts.append(self._stringify_breaking())
        parts.append(self._stringify_footers())

        return "\n".join(parts)

    def _stringify_header(self):
        if (self.header['scope'] != ""
             and not self.breaking["flag"]):
            header = fr"{self.header['type']}({self.header['scope']}): {self.header['msg']}"
        elif (self.header['scope'] != ""
             and self.breaking["flag"]):
            header = fr"{self.header['type']}({self.header['scope']})!: {self.header['msg']}"
        elif (self.header['scope'] == ""
              and not self.breaking["flag"]):
            header = fr"{self.header['type']}: {self.header['msg']}"
        elif (self.header['scope'] == ""
             and self.breaking["flag"]):
            header = fr"{self.header['type']}!: {self.header['msg']}"

        return header + "\n"

    def _stringify_body(self):
        if (len(self.body) > 0):
            return "\n".join(self.body)
        else:
            return ""

    def _stringify_breaking(self):
        if (self.breaking['msg'] == ""):
            return ""
        else:
            return f"{self.breaking['label']}: {self.breaking['msg']}\n"

    def _stringify_footers(self):
        footers = []

        for footer in self.footers:
            footers.append(f"{footer['label']}: {footer['msg']}\n")

        return "".join(footers)

    def __repr__(self, raw):
        return fr"ConventionalCommit(msg={self.raw})"


def _list_to_option_re(list):
    return fr"({'|'.join(list)})"


def _parse_commit(msg):
    """Parse a conventional commit message.

    Parse a conventional commit message according to the
    specification, including user defined types, scopes, and footers.

    BNF for conventional commit (v1.0.0):
        type :: ( feat | fix | 'user defined types' )
        scope :: ( '(' 'user defined scopes' ')' )
        header-breaking-flag :: !
        header-sep :: ': '
        header-msg :: .*
        header :: type scope? header-breaking-flag? header-sep header-msg
        breaking-label :: ( BREAKING CHANGE | BREAKING-CHANGE )
        breaking-sep :: ': '
        breaking-msg :: .*
        breaking :: breaking-label breaking-sep breaking-msg
        footer-label :: ( 'user defined footers' )
        footer-sep :: ': '
        footer-msg :: .*
        footer :: footer-label footer-sep footer-msg
        line :: .*
        newline :: '\n'
        skip :: newline newline
        par :: ( line newline )+
        body :: skip par+
        commit-msg :: header body? breaking? footer*
    """
    pp.ParserElement.defaultWhitespaceChars = ("\t")

    types = [
        'ci',
        'docs',
        'feat',
        'fix',
        'perf',
        'refactor',
        'style',
        'test',
    ]

    scopes = [
        'foo',
        'bar',
        'baz',
        'parser',
    ]

    footers = [
        'Signed-Off-By',
    ]

    msg_obj = {
        'header': {
            'type': '',
            'scope': '',
            'msg': '',
            'len': 0,
        },
        'body': {
            'paragraphs': [],
            'msg': '',
            'll': 0,
        },
        'breaking': {
            'flag': False,
            'label': '',
            'msg': '',
        },
        'footers': [],
    }

    def _header_handler(s, loc, tokens):
        tokens[0].append(tokens[0].pop()[0])
        msg_obj['len'] = len("".join(tokens[0]))

    def _header_type_handler(s, loc, tokens):
        msg_obj['header']['type'] = tokens[0]

    def _header_scope_handler(s, loc, tokens):
        msg_obj['header']['scope'] = tokens[0].lstrip("(").rstrip(")")

    def _header_msg_handler(s, loc, tokens):
        msg_obj['header']['msg'] = tokens[0][0].strip()

    def _breaking_flag_handler(s, loc, tokens):
        if (tokens[0] == '!'):
            msg_obj['breaking']['flag'] = True

    def _breaking_handler(s, loc, tokens):
        msg_obj['breaking']['label'] = tokens[0][0]
        msg_obj['breaking']['msg'] = tokens[0][2][0].strip()

    def _footer_handler(s, loc, tokens):
        for footer in tokens:
            msg_obj['footers'].append({
                'label': footer[0],
                'msg': footer[2][0].strip(),
            })

    def _body_handler(s, loc, tokens):
        nll = False
        par = []
        for line in tokens:
            if (nll and line == "\n"):
                msg_obj['body']['paragraphs'].append("".join(par))
                par = []
            else:
                par.append(line)

            if (line == "\n"):
                nll = True
            else:
                nll = False

            if msg_obj['body']['ll'] < len(line):
                msg_obj['body']['ll'] = len(line)

    eos = pp.StringEnd()

    type = pp.Regex(_list_to_option_re(types)).setResultsName("type", listAllMatches=True).setParseAction(_header_type_handler)
    scope = pp.Regex(r"\(" + _list_to_option_re(scopes) + r"\)").setResultsName("scope", listAllMatches=True).setParseAction(_header_scope_handler)
    header_breaking_flag = pp.Regex(r"!").setResultsName("header-breaking-flag", listAllMatches=True).setParseAction(_breaking_flag_handler)
    header_sep = pp.Regex(r": ")
    newline = pp.LineEnd().suppress()
    header_msg = pp.Group(~newline + ~eos + pp.Regex(r".*")).setResultsName("header-msg", listAllMatches=True).setParseAction(_header_msg_handler)
    header = pp.Group(
        type
        + pp.Optional(scope)
        + pp.Optional(header_breaking_flag)
        + header_sep
        + header_msg
    ).setResultsName("header", listAllMatches=True).setParseAction(_header_handler)

    breaking_label = pp.Regex(r"(BREAKING CHANGE|BREAKING-CHANGE)").setResultsName("breaking-label", listAllMatches=True)
    breaking_sep = pp.Regex(r": ")
    breaking_msg = pp.Group(~newline + ~eos + pp.Regex(r".*")).setResultsName("breaking-msg", listAllMatches=True)
    breaking = pp.Group(
        breaking_label
        + breaking_sep
        + breaking_msg
    ).setResultsName("breaking", listAllMatches=True).setParseAction(_breaking_handler)

    footer_label = pp.Regex(_list_to_option_re(footers)).setResultsName("footer-label", listAllMatches=True)
    footer_sep = pp.Regex(r": ")
    footer_msg = pp.Group(~newline + ~eos + pp.Regex(r".*")).setResultsName("footer-msg", listAllMatches=True)
    footer = pp.Group(
        footer_label
        + footer_sep
        + footer_msg
    ).setResultsName("footers", listAllMatches=True).setParseAction(_footer_handler)

    footers = pp.Group(breaking ^ footer)

    line = pp.Regex(r".*")
    bnewline = pp.LineEnd()
    skip = bnewline + bnewline
    par = pp.OneOrMore(~eos + ~footers + ~bnewline + line + bnewline)
    body = skip + pp.OneOrMore(~eos + ~footers + par + pp.Optional(bnewline)).setParseAction(_body_handler)

    commit_msg = (
        header
        + pp.Optional(body)
        + pp.Optional(breaking)
        + pp.ZeroOrMore(footer)
    ).setResultsName("commit-msg", listAllMatches=True)

    commit_msg.parseString(msg)

    return msg_obj
