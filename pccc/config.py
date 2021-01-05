"""pccc configuration functions."""

import argparse

import toml


def _create_argument_parser():
    """Create an argparse argument parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        # "commit",
        dest="commit",
        type=str,
        default="-",
        nargs="?",
        help="Commit message file.",
    )
    parser.add_argument(
        "-c",
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
        default=50,
        help="Maximum length of commit header.  Default is 50.",
    )
    parser.add_argument(
        "-b",
        "--body-length",
        dest="body_length",
        type=int,
        default=72,
        help="Maximum length of a body line.  Default is 72.",
    )
    parser.add_argument(
        "-s",
        "--spell-check",
        dest="spell_check",
        default=False,
        action="store_true",
        help="Spell check the commit.  Default is false.",
    )
    parser.add_argument(
        "-w",
        "--rewrap",
        dest="rewrap",
        default=False,
        action="store_true",
        help="Rewrap the body commit, regardless of line length." "  Default is false.",
    )
    parser.add_argument(
        "-r",
        "--repair",
        dest="repair",
        default=False,
        action="store_true",
        help="Repair the body commit as necessary; implies spell check and rewrap."
        "  Default is false.",
    )
    parser.add_argument(
        "-T",
        "--types",
        dest="types",
        type=lambda s: [item.strip() for item in s.split(",")],
        help="List (comma delimited) of allowable types for the type field"
        " of header.  Default is `['fix', 'feat']`.",
    )
    parser.add_argument(
        "-S",
        "--scopes",
        dest="scopes",
        type=lambda s: [item.strip() for item in s.split(",")],
        help="List (comma delimited) of allowable scopes for the scope field"
        " of header.  Default is an empty list.",
    )
    parser.add_argument(
        "-F",
        "--footers",
        dest="footers",
        type=lambda s: [item.strip() for item in s.split(",")],
        help="List (comma delimited) of allowable footer tokens for the"
        " commit footers.  Default is an empty list.",
    )
    parser.add_argument(
        "-R",
        "--required-footers",
        dest="required_footers",
        type=lambda s: [item.strip() for item in s.split(",")],
        help="List (comma delimited) of required footer tokens for the"
        " commit footers.  Default is an empty list.",
    )

    return parser


def _load_configuration_file(filename="./pyproject.toml"):
    """Load a configuration file, using the [tool.pccc] section.

    Parameters
    ----------
    filename : string (optional)
        Configuration file to load.

    Returns
    -------
    dict
       Configuration option keys and values.
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

    return config["tool"]["pccc"]


def _update_option(orig, new):
    """Update settings dict."""
    if new:
        return new
    else:
        return orig


def get_configuration_options():
    """Load configuration options.

    Load configuration options from defaults, file, then CLI, with
    later values overriding previous values.

    Returns
    -------
    dict
        Configuration keys and values.
    """
    # Parse the CLI options to make configuration file path available.
    args = _create_argument_parser().parse_args()

    # Defaults.
    options = {}
    options["commit"] = ""
    options["config_file"] = "./pyproject.toml"
    options["header_length"] = 50
    options["body_length"] = 72
    options["spell_check"] = False
    options["rewrap"] = False
    options["repair"] = False
    options["types"] = ["feat", "fix"]
    options["scopes"] = []
    options["footers"] = []
    options["required_footers"] = []

    # Configuration file; override defaults.
    options["config_file"] = _update_option(
        options["config_file"],
        args.config_file,
    )

    try:
        file_options = _load_configuration_file(options["config_file"])

        options["header_length"] = _update_option(
            options["header_length"],
            file_options["header_length"],
        )
        options["body_length"] = _update_option(
            options["body_length"],
            file_options["body_length"],
        )
        options["spell_check"] = _update_option(
            options["spell_check"],
            file_options["spell_check"],
        )
        options["rewrap"] = _update_option(
            options["rewrap"],
            file_options["rewrap"],
        )
        options["repair"] = _update_option(
            options["repair"],
            file_options["repair"],
        )
        options["types"] = _update_option(
            options["types"],
            file_options["types"],
        )
        options["scopes"] = _update_option(
            options["scopes"],
            file_options["scopes"],
        )
        options["footers"] = _update_option(
            options["footers"],
            file_options["footers"],
        )
        options["required_footers"] = _update_option(
            options["required_footers"],
            file_options["required_footers"],
        )
    except toml.TomlDecodeError:
        print(
            f"Unable to load configuration file {options['config_file'],}"
            f" using defaults and CLI options."
        )

    # CLI options; override configuration file.
    options["commit"] = args.commit
    options["header_length"] = _update_option(
        options["header_length"],
        args.header_length,
    )
    options["body_length"] = _update_option(
        options["body_length"],
        args.body_length,
    )
    options["spell_check"] = _update_option(
        options["spell_check"],
        args.spell_check,
    )
    options["rewrap"] = _update_option(
        options["rewrap"],
        args.rewrap,
    )
    options["repair"] = _update_option(
        options["repair"],
        args.repair,
    )
    options["types"] = _update_option(
        options["types"],
        args.types,
    )
    options["scopes"] = _update_option(
        options["scopes"],
        args.scopes,
    )
    options["footers"] = _update_option(
        options["footers"],
        args.footers,
    )
    options["required_footers"] = _update_option(
        options["required_footers"],
        args.required_footers,
    )

    return options
