"""Manage Dataverse aliases."""

import argparse

from ibridges.cli.base import BaseCliCommand

from ibridgescontrib.ibridgesdvn.dvn_config import DVN_CONFIG_FP, DVNConf, show_available


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
        """Command."""
        raise NotImplementedError("dv-setup is not available in the iBridges shell.")


    @classmethod
    def run_command(cls, args):
        """Create, delete, or list Dataverse aliases."""
        parser = cls.get_parser(argparse.ArgumentParser)
        dvn_conf = DVNConf(DVN_CONFIG_FP, parser)

        if not (args.url or args.alias or args.delete):
            show_available(dvn_conf)
            return

        if args.delete:
            dvn_conf.delete_alias(args.alias)
            show_available(dvn_conf)
            return

        if args.url is None:
            parser.error("Supply the URL to the Dataverse server to set the alias.")

        if not dvn_conf.is_valid_url(args.url):
            parser.error(f"Supplied URL '{args.url}' is not a valid URL.")

        if args.url in dvn_conf.dvns:
            dvn_conf.update_alias(args.url, args.alias)
        else:
            dvn_conf.add_dataverse(args.url, alias=args.alias)

        show_available(dvn_conf)
