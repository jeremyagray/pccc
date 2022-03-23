======
pccc
======

The Python Conventional Commit Checker.

.. image:: https://badge.fury.io/py/pccc.svg
   :target: https://badge.fury.io/py/pccc
   :alt: PyPI Version
.. image:: https://readthedocs.org/projects/pccc/badge/?version=latest
   :target: https://pccc.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

Description
===========

pccc is a PyParsing based grammar and script for parsing and verifying
a commit message is a conventional commit.  The default grammar
follows the `specification
<https://www.conventionalcommits.org/en/v1.0.0/#specification>`_, but
allows for the definition of types in addition to ``feat`` and ``fix``
and for the definition of project specific scopes and footers in
compliance with the specification.  The maximum line lengths of the
commit header and commit body and spelling can also be checked.

Currently, the script interface will load configuration options and a
commit message and attempt to parse it.  If there are no parse
exceptions, it will return 0, otherwise 1.  This interface should be
usable at the git ``commit-msg`` hook stage now.  It can also be
configured to ignore certain automatically generated commits (from
``git pull`` for instance) if it is not desirable or possible to
generate those commits as conventional commits (preferable).

Parsing Grammar
===============

Github Closes Issue Syntax

* KEYWORD = '(close[ds]?|fix(?:es|ed)?|resolve[ds]?)'
* OWNER = '^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$'
* REPOSITORY = '^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$'
* ISSUE-NUMBER = '#\d+'
* Single issue in same repository:  KEYWORD #ISSUE-NUMBER
* Single issue in different repository:  KEYWORD OWNER/REPOSITORY ISSUE-NUMBER
* Multiple issues: use full syntax for each issue

The parser in ``pccc`` requires separating multiple issues on the ``Github-issues`` line with ", ".

See:

#. https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue/
#. https://github.com/shinn/github-username-regex/

Roadmap
=======

#. Implement simple output reformatting, with configuration options
   and validation functions, operating in the validation/reformatting
   mode described previously.  (target: 0.6.0)

   * footer separator as ": " or " #"
   * "BREAKING-CHANGE" or "BREAKING CHANGE"
   * set breaking flag (!) and/or "BREAKING-CHANGE"
   * correct token capitalization ("BREAKING-CHANGE" not
     "breaking-change" or "Breaking-Change"; "Signed-off-by" not
     "Signed-Off-By" or "signed-off-by")

#. Implement partial parsing on failure for correction and improved
   exception handling. (target: 0.7.0 or later)

   * header partial parsing
   * body partial parsing
   * breaking change partial parsing
   * footer partial parsing

#. Feature freeze, strict semantic versioning, and finish alpha and
   beta. (from 0.7.0 onward; first stable will be at 1.0.0)

#. Implement custom hooks for handling per-project footers. (target:
   2.0.0 or later)

Installation
============

Install pccc with::

  pip install pccc
  pip freeze > requirements.txt

or add as a poetry dev-dependency.

If you desire a package locally built with poetry, download the
source, change the appropriate lines in ``pyproject.toml``, and
rebuild.

To use as a git ``commit-msg`` hook, copy the script ``pccc`` to
``.git/hooks/commit-msg`` and set the file as executable or integrate
the script or module into your existing ``commit-msg`` hook.  ``pccc``
relies on ``git`` setting the current working directory of the script
to the root of the repository (where ``pyproject.toml`` or
``package.json`` typically lives).  If this is not the repository
default, pass the configuration file path as an argument or symlink
from the current working directory to an appropriate configuration
file.

Usage
=====

Console::

  pccc COMMIT_MSG
  cat COMMIT_MSG | pccc

In Python::

  >>> import pccc
  >>> ccr = pccc.ConventionalCommitRunner()
  >>> ccr.options.load()
  >>> ccr.raw = "some commit message"
  >>> ccr.clean()
  >>> ccr.parse()
  >>> if ccr.exc == None:
  ...     print(ccr)

See the source and `documentation
<https://pccc.readthedocs.io/en/latest/>`_ for more information.

Configuration
=============

See ``pccc.toml`` for an example ``[tool.pccc]`` section that may be
copied into a ``pyproject.toml`` file.  The same entries may be used
in a ``pccc`` entry in ``package.json`` for JavaScript/TypeScript
projects.

Copyright and License
=====================

SPDX-License-Identifier: `GPL-3.0-or-later
<https://spdx.org/licenses/GPL-3.0-or-later.html>`_

pccc, the Python Conventional Commit Checker.
Copyright (C) 2020-2021 `Jeremy A Gray <jeremy.a.gray@gmail.com>`_.

This program is free software: you can redistribute it and/or modify
it under the terms of the `GNU General Public License
<https://www.gnu.org/licenses/gpl-3.0.html>`_ as published by the Free
Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the `GNU General Public License
<https://www.gnu.org/licenses/gpl-3.0.html>`_ along with this program.
If not, see https://www.gnu.org/licenses/.

Author
======

`Jeremy A Gray <jeremy.a.gray@gmail.com>`_
