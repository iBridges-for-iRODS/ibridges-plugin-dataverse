"""Main plugin file to show info."""

import argparse

from ibridges.cli.base import BaseCliCommand

from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf, show_available


class CliDvnAlias(BaseCliCommand):
    """Subcommand to get information from the server."""

    names = ["dv-setup"]
    description = "Print existing Dataverse configurations or create new ones."
    examples = ["some_alias https://demo.dataverse.nl", "other_alias --delete"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "alias",
            help="The new alias to be created",
            type=str,
            default=None,
            nargs="?",
        )
        parser.add_argument(
            "url", help="URL to the dataverse instance", type=str, default=None, nargs="?"
        )
        parser.add_argument(
            "--delete",
            "-d",
            help="Delete the alias.",
            action="store_true",
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run alias command not available in the shell."""
        raise NotImplementedError()

    @classmethod
    def run_command(cls, args):
        """Create and manage aliases in the CLI."""
        parser = cls.get_parser(argparse.ArgumentParser)
        dvn_conf = DVNConf(parser)

        # Show available and selected aliases.
        if args.alias is None:
            show_available(dvn_conf)
            return

        # Delete alias
        if args.delete:
            dvn_conf.delete_alias(args.alias)
            return

        if args.url is None:
            parser.error("Supply the URL to the Dataverse server to set the alias.")

        if not dvn_conf.is_valid_url(args.url):
            parser.error(f"Supplied URL '{args.url}' is not a valid URL.")

        dvn_conf.set_alias(args.alias, args.url)
        show_available(dvn_conf)
