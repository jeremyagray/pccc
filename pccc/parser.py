#!/usr/bin/env python

import pyparsing as pp


class ConventionalCommit():
    def __init__(self, msg):
        self.raw = msg

    def __str__(self):
        return self.raw

    def __repr__(self, raw):
        return fr"ConventionalCommit(msg={self.raw})"


def list_to_option_re(list):
    return fr"({'|'.join(list)})"


def parse_commit(msg):
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
        newline :: '\n'
        skip :: newline newline
        body-text :: .*
        body :: skip body-text
        breaking-label :: ( BREAKING CHANGE | BREAKING-CHANGE )
        breaking-sep :: ': '
        breaking-msg :: .*
        breaking :: breaking-label breaking-sep breaking-msg
        footer-sep :: ': '
        footer-msg :: .*
        footer :: ( 'user defined footers' ) footer-sep footer-msg
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

    END = pp.StringEnd()
    type = pp.Regex(list_to_option_re(types))
    print(type)
    scope = pp.Regex(r"\(" + list_to_option_re(scopes) + r"\)")
    # scope = pp.Regex(r"\((foo|bar|baz|parser)\)")
    print(scope)
    header_breaking_flag = pp.Regex(r"!")
    header_sep = pp.Regex(r": ")
    newline = pp.LineEnd().suppress()
    header_msg = pp.Group(~newline + ~END + pp.Regex(r".*"))
    header = pp.Group(
        type
        + pp.Optional(scope)
        + pp.Optional(header_breaking_flag)
        + header_sep
        + header_msg
    ).setResultsName("header", listAllMatches=True)

    breaking_label = pp.Regex(r"(BREAKING CHANGE|BREAKING-CHANGE)")
    breaking_sep = pp.Regex(r": ")
    breaking_msg = pp.Group(~newline + ~END + pp.Regex(r".*"))
    breaking = pp.Group(
        breaking_label
        + breaking_sep
        + breaking_msg
    ).setResultsName("breaking", listAllMatches=True)

    footer_label = pp.Regex(list_to_option_re(footers))
    footer_sep = pp.Regex(r": ")
    footer_msg = pp.Group(~newline + ~END + pp.Regex(r".*"))
    footer = pp.Group(
        footer_label
        + footer_sep
        + footer_msg
    ).setResultsName("footer", listAllMatches=True)

    footers = pp.Group(breaking ^ footer)

    skip = newline + newline
    body_text = pp.Group(
        ~END
        + ~footers
        + pp.Regex(r".*")
        + pp.ZeroOrMore(newline)
    )
    body = pp.Group(
        skip
        + pp.OneOrMore(body_text)
    ).setResultsName("body", listAllMatches=True).setName("body")

    commit_msg = (
        header
        + pp.Optional(body)
        + pp.Optional(breaking)
        + pp.ZeroOrMore(footer)
    )

    # parsed = commit_msg.parseString(msg)
    # searched = commit_msg.searchString(msg)
    # for item in parsed:
    #     print(item)
    # print(parsed.dump())
    # print(searched)
    return commit_msg.parseString(msg)
