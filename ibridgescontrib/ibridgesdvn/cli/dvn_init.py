"""Initialise and switch Dataverse configuration."""

import argparse
import sys
from getpass import getpass

from ibridges.cli.base import BaseCliCommand

from ibridgescontrib.ibridgesdvn.dvn_config import DVN_CONFIG_FP, DVNConf, show_available


class CliDvnInit(BaseCliCommand):
    """Initialize Dataverse configuration by providing a token."""

    names = ["dv-init"]
    description = "Store a Dataverse API token."
    examples = ["", "some_url", "some_alias"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "url_or_alias",
            help="URL or alias of the Dataverse server",
            type=str,
            nargs="?",
            default=None,
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Not available in shell mode."""
        raise NotImplementedError("dv-init is not available in the iBridges shell.")

    @classmethod
    def run_command(cls, args):
        """Initialize Dataverse configuration by storing an API token."""
        parser = cls.get_parser(argparse.ArgumentParser)
        dvn_conf = DVNConf(DVN_CONFIG_FP, parser)

        url_or_alias = args.url_or_alias

        try:
            url, _ = dvn_conf.get_entry(url_or_alias)
        except KeyError:
            # Treat input as URL and create a new Dataverse entry
            if not dvn_conf.is_valid_url(url_or_alias):
                parser.error(f"Supplied '{url_or_alias}' is neither a known alias nor a valid URL.")

            dvn_conf.add_dataverse(url_or_alias)
            url, _ = dvn_conf.get_entry(url_or_alias)

        # Set as current Dataverse
        dvn_conf.set_dvn(url)
        # Prompt for token
        if sys.stdin.isatty() or "ipykernel" in sys.modules:
            token = getpass(f"Your Dataverse token for {args.url_or_alias}: ")
        else:
            print(f"Your Dataverse token for {args.url_or_alias}: ")
            token = sys.stdin.readline().rstrip()

        # Store token
        dvn_conf.set_token(url, token)

        show_available(dvn_conf)



class CliDvnSwitch(BaseCliCommand):
    """Switch to another existing Dataverse configuration."""

    names = ["dv-switch"]
    description = "Switch to another Dataverse configuration by URL or alias."
    examples = ["some_url", "some_alias"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "url_or_alias",
            help="URL or alias of the Dataverse server",
            type=str,
            nargs="?",
            default=None,
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Not available in shell mode."""
        raise NotImplementedError("dv-switch is not available in the iBridges shell.")

    @classmethod
    def run_command(cls, args):
        """Switch to an existing Dataverse configuration."""
        parser = cls.get_parser(argparse.ArgumentParser)
        dvn_conf = DVNConf(DVN_CONFIG_FP, parser)

        dvn_conf.set_dvn(args.url_or_alias)
        show_available(dvn_conf)
