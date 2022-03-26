# ******************************************************************************
#
# pccc, the Python Conventional Commit Checker.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2020-2022 Jeremy A Gray <gray@flyquackswim.com>.
#
# ******************************************************************************

"""pccc configuration functions."""

import argparse
import json
import os
import re
import sys
import textwrap

import toml

from .exceptions import NotParseableError


class Config:
    """Class for accessing and loading pccc configuration options.

    Provides default values for all pccc configuration options and
    loading methods for reading ``pyproject.toml`` and CLI options.

    Attributes
    ----------
    commit : string, default="STDIN"
        Commit message location.
    config_file : string, default="pyproject.toml"
        Configuration file path.
    header_length : int, default=50
       Maximum header length.
    body_length : int, default=72
       Maximum body line length.
    repair : boolean, default=False
        Repair commit, implying spell check and wrap.
    wrap : boolean, default=False
        Wrap body and breaking change, if necessary.
    force_wrap : boolean, default=False
        Force wrap body and breaking change, regardless of length.
    spell_check : boolean, default=False
        Spell check commit message.
    ignore_generated_commits : boolean, default=False
        Ignore generated commits which match ``generated_commits``
        regular expressions.
    generated_commits : iterable of string, default=[]
        List of generated commits, as Python regular expressions.  For
        TOML files, it's probably best to use the multiline single
        quote strings to reduce escaping problems.
    types : iterable of string, default=["feat", "fix"]
        List of header types.
    scopes : iterable of string, default=[]
        List of header scopes.
    footers : iterable of string, default=[]
        List of footers.
    required_footers : iterable of string, default=[]
        List of required footers.
    """

    def __init__(
        self,
        commit="",
        config_file="pyproject.toml",
        header_length=50,
        body_length=72,
        repair=False,
        wrap=False,
        force_wrap=False,
        spell_check=False,
        ignore_generated_commits=False,
        generated_commits=[],
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
        # Configuration attributes.
        self.commit = commit
        self.config_file = config_file
        self.header_length = header_length
        self.body_length = body_length
        self.repair = repair
        self.wrap = wrap
        self.force_wrap = force_wrap
        self.spell_check = spell_check
        self.ignore_generated_commits = ignore_generated_commits
        self.generated_commits = generated_commits
        self.types = types
        self.scopes = scopes
        self.footers = footers
        self.required_footers = required_footers

        # Other attributes.
        self.format = "TOML"

    def __str__(self):
        """Stringify a ``Config()`` object.

        String representation of a ``Config()`` object, as the
        ``[tool.pccc]`` section of a ``pyproject.toml`` file or as the
        ``pccc`` entry of a JSON file such as ``package.json``.

        Parameters
        ----------
        fmt : string
           The output format.  Default is ``"TOML"``.  Currently
           supported values are ``"TOML"`` and ``"JSON"``.

        Returns
        -------
        string
            The current configuration, as the [tool.pccc] section of a
            ``pyproject.toml`` file.
        """
        if self.format == "JSON":
            # JSON, if requested.
            rs = json.dumps({"pccc": self.config_as_dict()}, indent=2)
        else:
            # TOML, by default.
            rs = toml.dumps({"pccc": self.config_as_dict()})

        return rs

    def __repr__(self):
        """Representation of a ``Config()`` object."""
        return (
            f'Config(commit="{self.commit}", '
            f'config_file="{self.config_file}", '
            f"header_length={self.header_length}, "
            f"body_length={self.body_length}, "
            f"repair={self.repair}, "
            f"wrap={self.wrap}, "
            f"force_wrap={self.force_wrap}, "
            f"spell_check={self.spell_check}, "
            f"ignore_generated_commits={self.ignore_generated_commits}, "
            f"generated_commits={self.generated_commits}, "
            f"types={self.types}, "
            f"scopes={self.scopes}, "
            f"footers={self.footers}, "
            f"required_footers={self.required_footers}, "
            f'format="{self.format}")'
        )

    def set_format(self, format):
        """Set the output format.

        Set the output format of ``Config().__str__()`` to either
        ``"TOML"`` or ``"JSON"``.
        """
        if format == "JSON":
            self.format = "JSON"
        else:
            self.format = "TOML"

        return

    def config_as_dict(self):
        """Convert a ``Config()`` object to a ``dict``.

        Convert a ``Config()`` object's configuration parameters to a
        ``dict`` for using in dumping TOML and JSON data.

        Returns
        -------
        dict
            A ``dict`` containing key-value pairs of the configuration
            parameters and their values.
        """
        return {
            "commit": self.commit,
            "header_length": self.header_length,
            "body_length": self.body_length,
            "repair": self.repair,
            "wrap": self.wrap,
            "force_wrap": self.force_wrap,
            "spell_check": self.spell_check,
            "ignore_generated_commits": self.ignore_generated_commits,
            "generated_commits": self.generated_commits,
            "types": self.types,
            "scopes": self.scopes,
            "footers": self.footers,
            "required_footers": self.required_footers,
        }

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
        """
        # Parse the CLI options to make configuration file path available.
        args = _create_argument_parser().parse_args(argv)

        # Configuration file; override defaults.
        if args.config_file is not None:
            self.config_file = args.config_file

        # Load the configuration file values.
        self.update(**_load_file(self.config_file))

        # Load the CLI configuration values.
        self.update(**vars(args))

        return


def _determine_file_format(filename):
    """Determine the format of a configuration file.

    Determine the format of a configuration file by attempting to
    parse the file's contents as TOML, JSON, YAML, and finally BespON,
    in that order.  Returns the format or raises ``ValueError`` on
    failure to determine the format.

    Parameters
    ----------
    filename : string
        Configuration file name.

    Returns
    -------
    format : string
       The file format, one of ``toml``, ``json``, ``yaml``, or
       ``bespon``.

    Raises
    ------
    ValueError
        Raised if the format of the file does not appear to match any
        of the defined formats.
    FileNotFoundError
        Raised if the configuration file does not exist or is not
        readable.
    """
    contents = ""
    try:
        with open(filename, "r") as file:
            contents = file.read()
    except FileNotFoundError as error:
        print(f"{error.strerror}: {error.filename}")
        raise

    try:
        toml.loads(contents)
        return "toml"
    except toml.TomlDecodeError:
        pass

    try:
        json.loads(contents)
        return "json"
    except json.JSONDecodeError:
        pass

    # Not implemented.
    # try:
    #     yaml.loads(contents)
    #     return "yaml"
    # except yaml.YamlDecodeError:
    #     pass

    # Not implemented.
    # try:
    #     bespon.loads(contents)
    #     return "bespon"
    # except bespon.BespONDecodeError:
    #     pass

    raise ValueError("Configuration file format not recognized")


def _load_file(filename=None):
    """Load a configuration file.

    Load a configuration file, defaulting to the first loadable file
    of ``pyproject.toml``, ``pccc.toml``, ``package.json``,
    ``pccc.json``, ``pccc.yaml``, ``pccc.yml``, and finally
    ``pccc.besp``.  If a file is specified, it will be prepended to
    the default list and processed identically.  The first file that
    exists and loads will be used.  If no usable file is found,
    default configuration values will be used.

    Note that this loader does not associate file formats and
    extensions; if a file format is recognized and is different than
    that purported by the extension, it will still load (i.e. it will
    load TOML from ``package.json``, etc.).

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
        file, but should only be raised if the file changes between
        format detection and loading.
    TomlDecodeError
        Raised if there are problems decoding a TOML configuration
        file, but should only be raised if the file changes between
        format detection and loading.
    FileNotFoundError
        Raised if the configuration file does not exist or is not
        readable, but should only be raised if the file changes
        between format detection and loading.
    """
    options = {}
    files = (
        "pyproject.toml",
        "pccc.toml",
        "package.json",
        "pccc.json",
        "pccc.yaml",
        "pccc.yml",
        "pccc.besp",
    )
    if filename:
        files = (filename,) + files

    for file in files:
        try:
            format = _determine_file_format(file)
        except (
            FileNotFoundError,
            ValueError,
        ) as error:
            print(error)
            continue

        if format == "toml":
            return _load_toml_file(file)
        elif format == "json":
            return _load_json_file(file)
        # Not implemented.
        # elif format == "yaml":
        #     return _load_yaml_file(file)
        # elif format == "bespon":
        #     return _load_bespon_file(file)

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
        "ignore_generated_commits": None,
        "wrap": None,
        "force_wrap": None,
        "repair": None,
        "types": None,
        "scopes": None,
        "footers": None,
        "required_footers": None,
        "ignore_generated_commits": None,
        "generated_commits": None,
    }

    for (k, v) in config["pccc"].items():
        empty_options[k] = v

    return empty_options


def _load_toml_file(filename="pyproject.toml"):
    """Load a TOML configuration file.

    Load a TOML configuration file, returning the ``[pccc]`` section.
    If the file is ``pyproject.toml``, then the ``[tool.pccc]``
    section is returned.

    Parameters
    ----------
    filename : string (optional), default = "pyproject.toml"
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
        raise

    empty_options = {
        "commit": None,
        "config_file": None,
        "header_length": None,
        "body_length": None,
        "spell_check": None,
        "wrap": None,
        "force_wrap": None,
        "repair": None,
        "types": None,
        "scopes": None,
        "footers": None,
        "required_footers": None,
        "ignore_generated_commits": None,
        "generated_commits": None,
    }

    if "pyproject.toml" in filename:
        for (k, v) in config["tool"]["pccc"].items():
            empty_options[k] = v
    else:
        for (k, v) in config["pccc"].items():
            empty_options[k] = v

    return empty_options


def _load_yaml_file(filename="./pccc.yaml"):
    """Load a YAML configuration file, using the ``pccc`` entry.

    Load a YAML configuration file, returning options from the
    top-level ``pccc`` dictionary.

    Parameters
    ----------
    filename : string (optional), default="pccc.yaml"
        Configuration file to load.

    Returns
    -------
    dict : options
       Configuration option keys and values, with unset values
       explicitly set to ``None``.

    Raises
    ------
    YamlDecodeError
        Raised if there are problems decoding a YAML configuration
        file.
    FileNotFoundError
        Raised if the configuration file does not exist or is not
        readable.
    """
    raise NotImplementedError


def _load_bespon_file(filename="./pccc.besp"):
    """Load a BespON configuration file, using the ``pccc`` entry.

    Load a BespON configuration file, returning options from the
    top-level ``pccc`` dictionary.

    Parameters
    ----------
    filename : string (optional), default="pccc.besp"
        Configuration file to load.

    Returns
    -------
    dict : options
       Configuration option keys and values, with unset values
       explicitly set to ``None``.

    Raises
    ------
    BesponDecodeError
        Raised if there are problems decoding a BespON configuration
        file.
    FileNotFoundError
        Raised if the configuration file does not exist or is not
        readable.
    """
    raise NotImplementedError


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
        default="pyproject.toml",
        help="Path to configuration file.  Default is ``pyproject.toml``.",
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

    ignore_group = parser.add_mutually_exclusive_group()
    ignore_group.add_argument(
        "-i",
        "--ignore-generated-commits",
        dest="ignore_generate_commits",
        default=None,
        action="store_true",
        help="Ignore generated commits that match the patterns in"
        " ``generated_commits``.  Default is to check every commit.",
    )
    ignore_group.add_argument(
        "-I",
        "--no-ignore-generated-commits",
        dest="ignore_generated_commits",
        default=None,
        action="store_false",
        help="Do not ignore generated commits that match the patterns in"
        " ``generated_commits``.  Default is to check every commit.",
    )

    wrap_group = parser.add_mutually_exclusive_group()
    wrap_group.add_argument(
        "-w",
        "--wrap",
        dest="wrap",
        default=None,
        action="store_true",
        help="Wrap the body commit, if necessary." "  Default is no wrapping.",
    )
    wrap_group.add_argument(
        "-W",
        "--no-wrap",
        dest="wrap",
        default=None,
        action="store_false",
        help="Do not wrap the body commit." "  Default is no wrapping.",
    )

    force_wrap_group = parser.add_mutually_exclusive_group()
    force_wrap_group.add_argument(
        "-z",
        "--force-wrap",
        dest="force_wrap",
        default=None,
        action="store_true",
        help="Wrap the body commit, regardless of line length."
        "  Default is no force wrapping.",
    )
    force_wrap_group.add_argument(
        "-Z",
        "--no-force-wrap",
        dest="force_wrap",
        default=None,
        action="store_false",
        help="Do not wrap the body commit." "  Default is no force wrapping.",
    )

    repair_group = parser.add_mutually_exclusive_group()
    repair_group.add_argument(
        "-r",
        "--repair",
        dest="repair",
        default=None,
        action="store_true",
        help="Repair the body commit as necessary; implies spell check and wrap."
        "  Default is false.",
    )
    repair_group.add_argument(
        "-R",
        "--no-repair",
        dest="repair",
        default=None,
        action="store_false",
        help="Do not repair the body commit; implies no spell check and no"
        " wrap.  Default is false.",
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
        # "a" is for automatic.
        "-a",
        "--generated-commits",
        dest="generated_commits",
        default=None,
        type=_field_list_handler,
        help="List (comma delimited) of Python regular expressions that"
        " match generated commits that should be ignored.  Mind the shell"
        " escaping.  Default is ``[]``.",
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

Copyright (C) 2021-2022 Jeremy A Gray <jeremy.a.gray@gmail.com>.

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
