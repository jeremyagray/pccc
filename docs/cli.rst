.. SPDX-License-Identifier: GPL-3.0-or-later
..
.. pccc, the Python Conventional Commit Checker.
.. Copyright (C) 2020-2021 Jeremy A Gray <jeremy.a.gray@gmail.com>.

CLI Arguments
=============

usage: pccc.py [-h] [--show-warranty] [--show-license] [-o CONFIG_FILE]
               [-l HEADER_LENGTH] [-b BODY_LENGTH] [-c | -C] [-i | -I] [-w | -W]
               [-r | -R] [-t TYPES] [-a GENERATED_COMMITS] [-s SCOPES]
               [-f FOOTERS] [-g REQUIRED_FOOTERS]
               [commit]

This program comes with ABSOLUTELY NO WARRANTY; for details type ``pccc --show-
warranty``. This is free software, and you are welcome to redistribute it under
certain conditions; type ``pccc --show-license`` for details.

positional arguments:
  commit                Commit message file.

optional arguments:
  -h, --help            show this help message and exit
  --show-warranty       Show warranty information.
  --show-license        Show license information.
  -o CONFIG_FILE, --config-file CONFIG_FILE
                        Path to configuration file. Default is ./pyproject.toml.
  -l HEADER_LENGTH, --header-length HEADER_LENGTH
                        Maximum length of commit header. Default is 50.
  -b BODY_LENGTH, --body-length BODY_LENGTH
                        Maximum length of a body line. Default is 72.
  -c, --spell-check     Spell check the commit. Default is no spell checking.
  -C, --no-spell-check  Do not spell check the commit. Default is no spell
                        checking.
  -i, --ignore-generated-commits
                        Ignore generated commits that match the patterns in
                        ``generated_commits``. Default is to check every commit.
  -I, --no-ignore-generated-commits
                        Do not ignore generated commits that match the patterns
                        in ``generated_commits``. Default is to check every
                        commit.
  -w, --rewrap          Rewrap the body commit, regardless of line length.
                        Default is no rewrapping.
  -W, --no-rewrap       Do not rewrap the body commit, regardless of line
                        length. Default is no rewrapping.
  -r, --repair          Repair the body commit as necessary; implies spell check
                        and rewrap. Default is false.
  -R, --no-repair       Do not repair the body commit; implies no spell check
                        and no rewrap. Default is false.
  -t TYPES, --types TYPES
                        List (comma delimited) of allowable types for the type
                        field of header. Default is `['fix', 'feat']`.
  -a GENERATED_COMMITS, --generated-commits GENERATED_COMMITS
                        List (comma delimited) of Python regular expressions
                        that match generated commits that should be ignored.
                        Mind the shell escaping. Default is ``[]``.
  -s SCOPES, --scopes SCOPES
                        List (comma delimited) of allowable scopes for the scope
                        field of header. Default is an empty list.
  -f FOOTERS, --footers FOOTERS
                        List (comma delimited) of allowable footer tokens for
                        the commit footers. Default is an empty list.
  -g REQUIRED_FOOTERS, --required-footers REQUIRED_FOOTERS
                        List (comma delimited) of required footer tokens for the
                        commit footers. Default is an empty list.
