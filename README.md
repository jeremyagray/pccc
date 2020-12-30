# pccc

The Python Conventional Commit Checker.

## What is pccc?

pccc is a PyParsing based grammar and script for parsing and verifying
a commit message is a conventional commit.  The default grammar
follows the
[specification](https://www.conventionalcommits.org/en/v1.0.0/#specification),
but allows for the definition of types in addition to `feat` and `fix`
and for the definition of project specific scopes and footers in
compliance with the specification.  The maximum line lengths of the
commit header and commit body and spelling can also be checked.

## Installation

```
pip install pccc
```
or add as a poetry dev-dependency.

## Usage

Console:

```
pccc COMMIT_MSG
```

## Copyright and License

SPDX-License-Identifier: GPL-3.0-or-later

pccc, the Python Conventional Commit Checker.
Copyright (C) 2020 Jeremy A Gray <jeremy.a.gray@gmail.com>.

This program is free software: you can redistribute it and/or modify
it under the terms of the [GNU General Public License](LICENSE) as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the [GNU General Public
License](LICENSE) along with this program.  If not, see
[https://www.gnu.org/licenses/](https://www.gnu.org/licenses/).

## Author

Jeremy A Gray <jeremy.a.gray@gmail.com>
