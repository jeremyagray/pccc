# SPDX-License-Identifier: GPL-3.0-or-later
#
# pccc, the Python Conventional Commit Checker.
# Copyright (C) 2020-2021 Jeremy A Gray <jeremy.a.gray@gmail.com>.
"""pccc configuration functions."""

import argparse
import json
import os
import re

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
    spell_check : boolean
      Spell check header and body; default is ``False``.
    rewrap : boolean
      Rewrap body; default is ``False``.
    repair : boolean
      Repair commit, implying spell check and rewrap; default is ``False``.
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
        spell_check=False,
        rewrap=False,
        repair=False,
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
        self.spell_check = spell_check
        self.rewrap = rewrap
        self.repair = repair
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
        if self.spell_check:
            rs += "spell_check = true\n"
        else:
            rs += "spell_check = false\n"
        if self.rewrap:
            rs += "rewrap = true\n"
        else:
            rs += "rewrap = false\n"
        if self.repair:
            rs += "repair = true\n"
        else:
            rs += "repair = false\n"
            rs += "\n"
            rs += "types = [\n" + "\n".join(
                map(lambda item: f'  "{item}",', self.types)
            )
        if len(self.types):
            rs += "\n]\n\n"
        else:
            rs += "]\n\n"
            rs += "scopes = [\n" + "\n".join(
                map(lambda item: f'  "{item}",', self.scopes)
            )
        if len(self.scopes):
            rs += "\n]\n\n"
        else:
            rs += "]\n\n"
            rs += "footers = [\n" + "\n".join(
                map(lambda item: f'  "{item}",', self.footers)
            )
        if len(self.footers):
            rs += "\n]\n\n"
        else:
            rs += "]\n\n"
            rs += "required_footers = [\n" + "\n".join(
                map(lambda item: f'  "{item}",', self.required_footers)
            )
        if len(self.required_footers):
            rs += "\n]"
        else:
            rs += "]"

        return rs

    def __repr__(self):
        """Representation of a ``Config()`` object."""
        return (
            f'Config(commit="{self.commit}", '
            f'config_file="{self.config_file}", '
            f"header_length={self.header_length}, "
            f"body_length={self.body_length}, "
            f"spell_check={self.spell_check}, "
            f"rewrap={self.rewrap}, "
            f"repair={self.repair}, "
            f"types={self.types}, "
            f"scopes={self.scopes}, "
            f"footers={self.footers}, "
            f"required_footers={self.required_footers})"
        )

    def update(self, *args, **kwargs):
        """Update a configuration.

        Return a new configuration object from the attributes of self
        combined with the key/value pairs provided, ignoring any keys
        that are not attributes and values that are ``None``.  The
        provided key/value pairs override the original values in self.

        Parameters
        ----------
        kwargs : dict
           Key/value pairs of configuration options.

        Returns
        -------
        object
            A new ``Config()`` object.
        """
        for (k, v) in kwargs.items():
            if hasattr(self, k) and v is not None:
                setattr(self, k, v)

        return

    def load_file(self):
        """Load configuration file.

        Load configuration options from file, with later values
        overriding previous values.

        Unset values are explicitly ``None`` at each level.

        Handles any ``FileNotFound``, ``JSONDecodeError``, or
        ``TomlDecodeError`` exceptions that arise during loading of
        configuration file by ignoring the file.
        """
        try:
            self.update(**_load_file(self.config_file))
        except (FileNotFoundError,):
            print(
                f"Unable to find configuration file {self.config_file},"
                " using defaults and CLI options."
            )
        except (
            json.JSONDecodeError,
            toml.TomlDecodeError,
        ):
            print(
                f"Unable to parse configuration file {self.config_file},"
                " using defaults and CLI options.\n"
                "Ensure that file format matches extension."
            )

        return

    def load(self):
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
        args = _create_argument_parser().parse_args()

        # Configuration file; override defaults.
        self.config_file = _update_file_option(
            self.config_file,
            args.config_file,
        )

        try:
            self.update(**_load_file(self.config_file))
        except (FileNotFoundError,):
            print(
                f"Unable to find configuration file {self.config_file},"
                " using defaults and CLI options."
            )
        except (
            json.JSONDecodeError,
            toml.TomlDecodeError,
        ):
            print(
                f"Unable to parse configuration file {self.config_file},"
                " using defaults and CLI options.\n"
                "Ensure that file format matches extension."
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


def _update_file_option(orig, new):
    """Update a file option.

    Update date a file option, if file new exists and is readable.
    """
    if new and os.path.exists(new):
        return new
    else:
        return orig


def _add_bool_arg(parser, name, short, default=None, help=""):
    parser.add_argument(
        "--" + name,
        "-" + short,
        dest=name,
        action="store_true",
        help=help,
    )
    parser.add_argument(
        "--no-" + name,
        "-" + short.upper(),
        dest=name,
        action="store_false",
        help=help,
    )
    parser.set_defaults(**{name: default})

    return


def _create_argument_parser():
    """Create an argparse argument parser."""
    parser = argparse.ArgumentParser()
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
    _add_bool_arg(
        parser,
        "spell-check",
        "c",
        default=None,
        help="Spell check the commit, or not.  Default is false.",
    )
    # parser.add_argument(
    #     "-s",
    #     "--spell-check",
    #     dest="spell_check",
    #     # type=bool,
    #     # default=False,
    #     default=None,
    #     action="store_true",
    #     help="Spell check the commit.  Default is false.",
    # )
    _add_bool_arg(
        parser,
        "rewrap",
        "w",
        default=None,
        help="Rewrap the body commit, or not, regardless of line length."
        "  Default is false.",
    )
    # parser.add_argument(
    #     "-w",
    #     "--rewrap",
    #     dest="rewrap",
    #     type=bool,
    #     # default=False,
    #     default=None,
    #     action="store_true",
    #     help="Rewrap the body commit, regardless of line length."
    #     "  Default is false.",
    # )
    _add_bool_arg(
        parser,
        "repair",
        "r",
        default=None,
        help="Repair the body commit, or not;"
        " implies spell check and rewrap.  Default is false.",
    )
    # parser.add_argument(
    #     "-r",
    #     "--repair",
    #     dest="repair",
    #     type=bool,
    #     # default=False,
    #     default=None,
    #     action="store_true",
    #     help="Repair the body commit as necessary; implies spell check and rewrap."
    #     "  Default is false.",
    # )
    parser.add_argument(
        "-t",
        "--types",
        dest="types",
        default=None,
        type=lambda s: [item.strip() for item in s.split(",")],
        help="List (comma delimited) of allowable types for the type field"
        " of header.  Default is `['fix', 'feat']`.",
    )
    parser.add_argument(
        "-s",
        "--scopes",
        dest="scopes",
        default=None,
        type=lambda s: [item.strip() for item in s.split(",")],
        help="List (comma delimited) of allowable scopes for the scope field"
        " of header.  Default is an empty list.",
    )
    parser.add_argument(
        "-f",
        "--footers",
        dest="footers",
        default=None,
        type=lambda s: [item.strip() for item in s.split(",")],
        help="List (comma delimited) of allowable footer tokens for the"
        " commit footers.  Default is an empty list.",
    )
    parser.add_argument(
        "-g",
        "--required-footers",
        dest="required_footers",
        default=None,
        type=lambda s: [item.strip() for item in s.split(",")],
        help="List (comma delimited) of required footer tokens for the"
        " commit footers.  Default is an empty list.",
    )

    return parser
