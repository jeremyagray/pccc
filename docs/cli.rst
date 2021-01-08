.. SPDX-License-Identifier: GPL-3.0-or-later
..
.. pccc, the Python Conventional Commit Checker.
.. Copyright (C) 2020-2021 Jeremy A Gray <jeremy.a.gray@gmail.com>.

CLI Arguments
=============

  usage: pccc.py [-h] [-o CONFIG_FILE] [-l HEADER_LENGTH] [-b BODY_LENGTH]
                 [--spell-check] [--no-spell-check] [--rewrap] [--no-rewrap]
                 [--repair] [--no-repair] [-t TYPES] [-s SCOPES] [-f FOOTERS]
                 [-g REQUIRED_FOOTERS]
                 [commit]

  positional arguments:
    commit                Commit message file.

  optional arguments:
    -h, --help            show this help message and exit
    -o CONFIG_FILE, --config-file CONFIG_FILE
                          Path to configuration file. Default is
                          ./pyproject.toml.
    -l HEADER_LENGTH, --header-length HEADER_LENGTH
                          Maximum length of commit header. Default is 50.
    -b BODY_LENGTH, --body-length BODY_LENGTH
                          Maximum length of a body line. Default is 72.
    --spell-check, -c     Spell check the commit. Default is false.
    --no-spell-check, -C  Spell check the commit. Default is false.
    --rewrap, -w          Rewrap the body commit, regardless of line length.
                          Default is false.
    --no-rewrap, -W       Rewrap the body commit, regardless of line length.
                          Default is false.
    --repair, -r          Repair the body commit as necessary; implies spell
                          check and rewrap. Default is false.
    --no-repair, -R       Repair the body commit as necessary; implies spell
                          check and rewrap. Default is false.
    -t TYPES, --types TYPES
                          List (comma delimited) of allowable types for the type
                          field of header. Default is `['fix', 'feat']`.
    -s SCOPES, --scopes SCOPES
                          List (comma delimited) of allowable scopes for the
                          scope field of header. Default is an empty list.
    -f FOOTERS, --footers FOOTERS
                          List (comma delimited) of allowable footer tokens for
                          the commit footers. Default is an empty list.
    -g REQUIRED_FOOTERS, --required-footers REQUIRED_FOOTERS
                          List (comma delimited) of required footer tokens for
                          the commit footers. Default is an empty list.
