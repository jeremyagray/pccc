# SPDX-License-Identifier: GPL-3.0-or-later
#
# pccc, the Python Conventional Commit Checker.
# Copyright (C) 2020-2021 Jeremy A Gray <jeremy.a.gray@gmail.com>.
"""pccc configuration functions."""

import argparse
import json
import os
import re
import sys
import textwrap

import toml


class Config:
    """Class for accessing and loading pccc configuration options.

    Provides default values for all pccc configuration options and
    loading methods for reading pyproject.toml and CLI options.

    Attributes
    ----------
    commit : string
        Commit message location; default is ``STDIN``.
    config_file : string
        Configuration file path; default is ``pyproject.toml``.
    header_length : int
       Maximum header length; default is 50.
    body_length : int
       Maximum body line length; default is 72.
    repair : boolean
      Repair commit, implying spell check and rewrap; default is ``False``.
    rewrap : boolean
      Rewrap body; default is ``False``.
    spell_check : boolean
      Spell check header and body; default is ``False``.
    types : [string]
        List of header types; default is ``['feat', 'fix']``.
    scopes : [string]
        List of header scopes; default is ``[]``.
    footers : [string]
        List of footers; default is ``[]``.
    required_footers : [string]
        List of required footers; default is ``[]``.
    """

    def __init__(
        self,
        commit="",
        config_file="./pyproject.toml",
        header_length=50,
        body_length=72,
        repair=False,
        rewrap=False,
        spell_check=False,
        types=["feat", "fix"],
        scopes=[],
        footers=[],
        required_footers=[],
    ):
        """Create a ``Config()`` object.

        Create a default ``Config()`` object.

        Returns
        -------
        object
            A Config() object.
        """
        self.commit = commit
        self.config_file = config_file
        self.header_length = header_length
        self.body_length = body_length
        self.repair = repair
        self.rewrap = rewrap
        self.spell_check = spell_check
        self.types = types
        self.scopes = scopes
        self.footers = footers
        self.required_footers = required_footers

    def __str__(self):
        """Stringify a ``Config()`` object.

        String representation of a ``Config()`` object, as the
        ``[tool.pccc]`` section of a pyproject.toml file.

        Returns
        -------
        string
            The current configuration, as the [tool.pccc] section of a
            ``pyproject.toml`` file.
        """
        rs = "[tool.pccc]\n"
        rs += "\n"
        rs += f"header_length = {self.header_length}\n"
        rs += f"body_length = {self.body_length}\n"

        if self.repair:
            rs += "repair = true\n"
        else:
            rs += "repair = false\n"

        if self.rewrap:
            rs += "rewrap = true\n"
        else:
            rs += "rewrap = false\n"

        if self.spell_check:
            rs += "spell_check = true\n"
        else:
            rs += "spell_check = false\n"

        rs += "\n"

        # rs += "types = [\n" + "\n".join(map(lambda item: f'  "{item}",', self.types))
        rs += "types = [\n" + ",\n".join(map(lambda item: f'  "{item}"', self.types))

        if len(self.types):
            rs += "\n]\n\n"
        else:
            rs += "]\n\n"

        rs += "scopes = [\n" + ",\n".join(map(lambda item: f'  "{item}"', self.scopes))

        if len(self.scopes):
            rs += "\n]\n\n"
        else:
            rs += "]\n\n"

        # rs += "footers = [\n" + "\n".join(
        #     map(lambda item: f'  "{item}",', self.footers)
        # )
        rs += "footers = [\n" + ",\n".join(
            map(lambda item: f'  "{item}"', self.footers)
        )

        if len(self.footers):
            rs += "\n]\n\n"
        else:
            rs += "]\n\n"

        # rs += "required_footers = [\n" + "\n".join(
        #     map(lambda item: f'  "{item}",', self.required_footers)
        # )
        rs += "required_footers = [\n" + ",\n".join(
            map(lambda item: f'  "{item}"', self.required_footers)
        )

        if len(self.required_footers):
            rs += "\n]\n"
        else:
            rs += "]\n"

        return rs

    def __repr__(self):
        """Representation of a ``Config()`` object."""
        return (
            f'Config(commit="{self.commit}", '
            f'config_file="{self.config_file}", '
            f"header_length={self.header_length}, "
            f"body_length={self.body_length}, "
            f"repair={self.repair}, "
            f"rewrap={self.rewrap}, "
            f"spell_check={self.spell_check}, "
            f"types={self.types}, "
            f"scopes={self.scopes}, "
            f"footers={self.footers}, "
            f"required_footers={self.required_footers})"
        )

    def update(self, *args, **kwargs):
        """Update a configuration.

        Update the current configuration object from the provided
        dictionary, ignoring any keys that are not attributes and
        values that are ``None``.  The provided key/value pairs
        override the original values in self.

        Parameters
        ----------
        kwargs : dict
           Key/value pairs of configuration options.
        """
        for (k, v) in kwargs.items():
            if hasattr(self, k) and v is not None:
                setattr(self, k, v)

        return

    def validate(self):
        """Validate a configuration.

        Validate the current configuration object to ensure compliance
        with the conventional commit specification.  Current checks
        include: ensure that 'fix' and 'feat' are present in the
        ``types`` list.

        Returns
        -------
        boolean
            True for a valid configuration, raises on invalid
            configuration.

        Raises
        ------
        ValueError
            Indicates a configuration value is incorrect.
        """
        if not ("fix" in self.types and "feat" in self.types):
            raise ValueError("Commit types must include 'fix' and 'feat'.")

        return True

    def load(self, argv=None):
        """Load configuration options.

        Load configuration options from defaults (class constructor),
        file (either default or specified on CLI), then CLI, with
        later values overriding previous values.

        Unset values are explicitly ``None`` at each level.

        Handles any ``FileNotFound``, ``JSONDecodeError``, or
        ``TomlDecodeError`` exceptions that arise during loading of
        configuration file by ignoring the file.
        """
        # Parse the CLI options to make configuration file path available.
        args = _create_argument_parser().parse_args(argv)

        # Configuration file; override defaults.
        if args.config_file is not None:
            self.config_file = args.config_file

        try:
            self.update(**_load_file(self.config_file))
        except (FileNotFoundError,):
            print(
                f"Unable to find configuration file {self.config_file},"
                " using defaults and CLI options."
            )
        except (json.JSONDecodeError,):
            print(
                f"Unable to parse configuration file {self.config_file}"
                " (default package.json), using defaults and CLI options.\n"
                "Ensure that file format matches extension."
            )
        except (toml.TomlDecodeError,):
            print(
                f"Unable to parse configuration file {self.config_file}"
                " (default pyproject.toml), using defaults and CLI options."
                "  Ensure that file format matches extension."
            )

        self.update(**vars(args))

        return


def _load_file(filename="./pyproject.toml"):
    """Load a configuration file, using the ``[tool.pccc]`` section.

    Load a ``pyproject.toml`` configuration file, using the
    ``[tool.pccc]`` section, or a ``package.json`` configuration file,
    using the ``pccc`` entry.  Will only load ``package.json`` if
    ``pyproject.toml`` is not available or if ``package.json`` is
    explicitly set as the configuration file.

    Parameters
    ----------
    filename : string (optional)
        Configuration file to load.

    Returns
    -------
    dict
       Configuration option keys and values, with unset values
       explicitly set to ``None``.

    Raises
    ------
    JSONDecodeError
        Raised if there are problems decoding a JSON configuration
        file.
    TomlDecodeError
        Raised if there are problems decoding a TOML configuration
        file.
    FileNotFoundError
        Raised if the configuration file does not exist or is not
        readable.
    """
    options = {}
    jsonRE = re.compile(r"^.*\.json$", re.IGNORECASE)

    if os.path.abspath(filename) == os.path.abspath("./pyproject.toml"):
        try:
            # Default to ``./pyproject.toml``.
            options = _load_toml_file(filename)
        except toml.TomlDecodeError:
            raise
        except FileNotFoundError:
            try:
                # Then try ``./package.json``.
                options = _load_json_file("./package.json")
            except json.JSONDecodeError:
                raise
            except FileNotFoundError:
                raise
    elif jsonRE.match(filename):
        try:
            # Well, if JSON is supplied, use it.
            options = _load_json_file(filename)
        except json.JSONDecodeError:
            raise
        except FileNotFoundError:
            raise
    else:
        try:
            # Last chance, parse filename as TOML.
            options = _load_toml_file(filename)
        except toml.TomlDecodeError:
            raise
        except FileNotFoundError:
            raise

    return options


def _load_json_file(filename="./package.json"):
    """Load a JSON configuration file, using the ``pccc`` entry.

    Load a ``package.json`` configuration file, returning the ``pccc``
    entry.

    Parameters
    ----------
    filename : string (optional)
        Configuration file to load.

    Returns
    -------
    dict
       Configuration option keys and values, with unset values
       explicitly set to ``None``.

    Raises
    ------
    JSONDecodeError
        Raised if there are problems decoding a JSON configuration
        file.
    FileNotFoundError
        Raised if the configuration file does not exist or is not
        readable.
    """
    try:
        with open(filename, "r") as file:
            config = json.load(file)
    except json.JSONDecodeError as error:
        lines = error.doc.split("\n")
        print(
            f"In configuration file {filename},"
            f" line {error.lineno}, column {error.colno}:"
        )
        print(lines[error.lineno - 1])
        print(error.msg)
        raise
    except FileNotFoundError as error:
        print(f"{error.strerror}: {error.filename}")
        raise

    empty_options = {
        "commit": None,
        "config_file": None,
        "header_length": None,
        "body_length": None,
        "spell_check": None,
        "rewrap": None,
        "repair": None,
        "types": None,
        "scopes": None,
        "footers": None,
        "required_footers": None,
    }

    for (k, v) in config["pccc"].items():
        empty_options[k] = v

    return empty_options


def _load_toml_file(filename="./pyproject.toml"):
    """Load a toml configuration file.

    Load a ``pyproject.toml`` configuration file, returning the
    ``[tool.pccc]`` section.

    Parameters
    ----------
    filename : string (optional)
        Configuration file to load.

    Returns
    -------
    dict
       Configuration option keys and values, with unset values
       explicitly set to ``None``.

    Raises
    ------
    TomlDecodeError
        Raised if there are problems decoding a TOML configuration
        file.
    FileNotFoundError
        Raised if the configuration file does not exist or is not
        readable.
    """
    try:
        with open(filename, "r") as file:
            config = toml.load(file)
    except toml.TomlDecodeError as error:
        lines = error.doc.split("\n")
        print(
            f"In configuration file {filename},"
            f" line {error.lineno}, column {error.colno}:"
        )
        print(lines[error.lineno - 1])
        print(error.msg)
        raise
    except FileNotFoundError as error:
        print(f"{error.strerror}: {error.filename}")
        print("trying package.json...")
        raise

    empty_options = {
        "commit": None,
        "config_file": None,
        "header_length": None,
        "body_length": None,
        "spell_check": None,
        "rewrap": None,
        "repair": None,
        "types": None,
        "scopes": None,
        "footers": None,
        "required_footers": None,
    }

    for (k, v) in config["tool"]["pccc"].items():
        empty_options[k] = v

    return empty_options


def _create_argument_parser():
    """Create an argparse argument parser."""
    parser = argparse.ArgumentParser(
        description="""\
This program comes with ABSOLUTELY NO WARRANTY; for details type
``pccc --show-warranty``.  This is free software, and you are welcome
to redistribute it under certain conditions; type ``pccc
--show-license`` for details.
""",
    )

    parser.add_argument(
        "--show-warranty",
        nargs=0,
        action=_ShowLicenseAction,
        help="Show warranty information.",
    )

    parser.add_argument(
        "--show-license",
        nargs=0,
        action=_ShowLicenseAction,
        help="Show license information.",
    )

    parser.add_argument(
        dest="commit",
        type=str,
        default="-",
        nargs="?",
        help="Commit message file.",
    )

    parser.add_argument(
        "-o",
        "--config-file",
        dest="config_file",
        type=str,
        default="./pyproject.toml",
        help="Path to configuration file.  Default is ./pyproject.toml.",
    )

    parser.add_argument(
        "-l",
        "--header-length",
        dest="header_length",
        type=int,
        # default=50,
        default=None,
        help="Maximum length of commit header.  Default is 50.",
    )

    parser.add_argument(
        "-b",
        "--body-length",
        dest="body_length",
        type=int,
        # default=72,
        default=None,
        help="Maximum length of a body line.  Default is 72.",
    )

    spell_group = parser.add_mutually_exclusive_group()
    spell_group.add_argument(
        "-c",
        "--spell-check",
        dest="spell_check",
        default=None,
        action="store_true",
        help="Spell check the commit.  Default is no spell checking.",
    )
    spell_group.add_argument(
        "-C",
        "--no-spell-check",
        dest="spell_check",
        # type=bool,
        # default=False,
        default=None,
        action="store_false",
        help="Do not spell check the commit.  Default is no spell checking.",
    )

    rewrap_group = parser.add_mutually_exclusive_group()
    rewrap_group.add_argument(
        "-w",
        "--rewrap",
        dest="rewrap",
        default=None,
        action="store_true",
        help="Rewrap the body commit, regardless of line length."
        "  Default is no rewrapping.",
    )
    rewrap_group.add_argument(
        "-W",
        "--no-rewrap",
        dest="rewrap",
        default=None,
        action="store_false",
        help="Do not rewrap the body commit, regardless of line length."
        "  Default is no rewrapping.",
    )

    repair_group = parser.add_mutually_exclusive_group()
    repair_group.add_argument(
        "-r",
        "--repair",
        dest="repair",
        default=None,
        action="store_true",
        help="Repair the body commit as necessary; implies spell check and rewrap."
        "  Default is false.",
    )
    repair_group.add_argument(
        "-R",
        "--no-repair",
        dest="repair",
        default=None,
        action="store_false",
        help="Do not repair the body commit; implies no spell check and no"
        " rewrap.  Default is false.",
    )

    parser.add_argument(
        "-t",
        "--types",
        dest="types",
        default=None,
        type=_field_list_handler,
        help="List (comma delimited) of allowable types for the type field"
        " of header.  Default is `['fix', 'feat']`.",
    )

    parser.add_argument(
        "-s",
        "--scopes",
        dest="scopes",
        default=None,
        type=_field_list_handler,
        help="List (comma delimited) of allowable scopes for the scope field"
        " of header.  Default is an empty list.",
    )

    parser.add_argument(
        "-f",
        "--footers",
        dest="footers",
        default=None,
        type=_field_list_handler,
        help="List (comma delimited) of allowable footer tokens for the"
        " commit footers.  Default is an empty list.",
    )

    parser.add_argument(
        "-g",
        "--required-footers",
        dest="required_footers",
        default=None,
        type=_field_list_handler,
        help="List (comma delimited) of required footer tokens for the"
        " commit footers.  Default is an empty list.",
    )

    return parser


class _ShowLicenseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        license = """\
pccc:  The Python Conventional Commit Checker.

Copyright (C) 2021 Jeremy A Gray <jeremy.a.gray@gmail.com>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
        print(
            "\n\n".join(
                list(
                    map(
                        lambda item: "\n".join(textwrap.wrap(item.strip(), 72)),
                        textwrap.dedent(license).strip().split("\n\n"),
                    )
                )
            )
        )

        sys.exit(0)


def _field_list_handler(s):
    if len(s) == 0:
        return []
    else:
        return [item.strip() for item in s.split(",")]
