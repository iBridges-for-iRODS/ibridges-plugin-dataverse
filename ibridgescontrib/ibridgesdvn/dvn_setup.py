"""Manage Dataverse aliases."""

import argparse
from ibridges.cli.base import BaseCliCommand

from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf, show_available


class CliDvnAlias(BaseCliCommand):
    """Create, delete, or list Dataverse aliases."""

    names = ["dv-setup"]
    description = "Print existing Dataverse configurations or create new ones."
    examples = ["some_alias https://demo.dataverse.nl", "other_alias --delete"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "alias",
            help="Alias to create or delete",
            type=str,
            nargs="?",
            default=None,
        )
        parser.add_argument(
            "url",
            help="URL of the Dataverse instance",
            type=str,
            nargs="?",
            default=None,
        )
        parser.add_argument(
            "--delete",
            "-d",
            help="Delete the alias instead of creating it",
            action="store_true",
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """This command is CLI-only."""
        raise NotImplementedError("dv-setup is not available in the iBridges shell.")


    @classmethod
    def run_command(cls, args):
        """Create, delete, or list Dataverse aliases."""
        parser = cls.get_parser(argparse.ArgumentParser)
        dvn_conf = DVNConf(parser)

        # No alias → list all
        if args.alias is None:
            show_available(dvn_conf)
            return

        # Delete alias
        if args.delete:
            dvn_conf.delete_alias(args.alias)
            show_available(dvn_conf)
            return

        # Creating alias requires URL
        if args.url is None:
            parser.error("Supply the URL to the Dataverse server to set the alias.")

        if not dvn_conf.is_valid_url(args.url):
            parser.error(f"Supplied URL '{args.url}' is not a valid URL.")

        # Create or update alias
        dvn_conf.set_alias(args.alias, args.url)
        show_available(dvn_conf)
