"""Initialise and switch Dataverse configuration."""

import argparse
import sys
from getpass import getpass

from ibridges.cli.base import BaseCliCommand

from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf, show_available

# ----------------------------------------------------------------------
# dv-init
# ----------------------------------------------------------------------

class CliDvnInit(BaseCliCommand):
    """Initialize Dataverse configuration by providing a token."""

    names = ["dv-init"]
    description = "Provide token and store for future use"
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
        dvn_conf = DVNConf(parser)

        # Select or create the Dataverse entry
        dvn_conf.set_dvn(args.url_or_alias)
        url, entry = dvn_conf.get_entry()

        # Prompt for token
        if sys.stdin.isatty() or "ipykernel" in sys.modules:
            token = getpass(f"Your Dataverse token for {args.url_or_alias}: ")
        else:
            print(f"Your Dataverse token for {args.url_or_alias}: ")
            token = sys.stdin.readline().rstrip()

        # Store token
        entry["token"] = token
        dvn_conf.dvns[url] = entry
        dvn_conf.save()

        show_available(dvn_conf)


# ----------------------------------------------------------------------
# dv-switch
# ----------------------------------------------------------------------

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
        dvn_conf = DVNConf(parser)

        dvn_conf.set_dvn(args.url_or_alias)
        show_available(dvn_conf)

