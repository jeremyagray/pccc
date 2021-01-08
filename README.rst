pccc
----

The Python Conventional Commit Checker.

What is pccc?
~~~~~~~~~~~~~

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
usable at the git ``commit-msg`` hook stage now.

Roadmap
~~~~~~~

#. 100% test coverage, with tests implemented before merging. (target:
   0.4.0)
#. Complete documentation integration and upload. (target: 0.4.0)
#. Integrate ``argparse`` help into documentation. (target: 0.4.0)
#. Insert license information into all source files. (target: 0.4.0)
#. Complete upload and build for setuptools/pip and poetry. (target:
   0.4.0)
#. Github issue template based off current ``tests/good/*.json``
   files, with guidelines. (target: 0.4.0)
#. Finish body wrapping. (target: 0.5.0)

   * fail if over
   * rewrap if over
   * do nothing if fine
   * rewrap if fine

#. Implement spell checking. (target: 0.6.0)

   * will not autocorrect
   * communication: kick back to editor on errors, with comment line
     to indicate acceptance

#. Implement simple reformatting. (target: 0.7.0)

   * footer separator as ": " and not " #"
   * "BREAKING-CHANGE" not "BREAKING CHANGE"
   * set breaking flag (!) and "BREAKING-CHANGE"
   * correct token capitalization ("BREAKING-CHANGE" not
     "breaking-change" or "Breaking-Change"; "Signed-off-by" not
     "Signed-Off-By" or "signed-off-by")

#. Implement partial parsing on failure for correction and improved
   exception handling. (target: 0.9.0 or later)

   * header partial parsing
   * body partial parsing
   * breaking change partial parsing
   * footer partial parsing

#. Implement custom hooks for handling per-project footers. (target:
   0.9.0 or later)

Installation
~~~~~~~~~~~~

Install pccc with::

  pip install pccc

or add as a poetry dev-dependency (TODO).

Usage
~~~~~

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

See the source and documentation for more information.

Configuration
~~~~~~~~~~~~~

See ``pccc.toml`` for an example ``[tool.pccc]`` section that may be
copied into a ``pyproject.toml`` file.

Copyright and License
~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~

`Jeremy A Gray <jeremy.a.gray@gmail.com>`_
