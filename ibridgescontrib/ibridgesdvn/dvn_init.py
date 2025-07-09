import sys
import argparse
from getpass import getpass

from ibridges.cli.base import BaseCliCommand
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf, show_available


class CliDvnInit(BaseCliCommand):
    """Subcommand to initialize ibridges."""

    names = ["dv-init"]
    description = "Provide token and store for future use"
    examples = ["", "some_url", "some_alias"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "url_or_alias",
            help="The URL to the Dataverse server.",
            type=str,
            default=None,
            nargs="?",
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        raise NotImplementedError()

    @classmethod
    def run_command(cls, args):
        """Initialize Dataverse configuration by providing token."""
        parser = cls.get_parser(argparse.ArgumentParser)
        dvn_conf = DVNConf(parser)
        dvn_conf.set_dvn(args.url_or_alias)
        dvn, entry = DVNConf(parser).get_entry()
        
        
        if sys.stdin.isatty() or "ipykernel" in sys.modules:
            token = getpass(f"Your Dataverse token for {args.url_or_alias} : ")
        else:
            print(f"Your Dataverse token for {args.url_or_alias} : ")
            token = sys.stdin.readline().rstrip()
        
        entry["token"] = token
        dvn_conf.save()
        show_available(dvn_conf)

class CliDvnSwitch(BaseCliCommand):
    """Subcommand to switch to Dataverse configuration."""

    names = ["dv-switch"]
    description = "Switch to another existing Dataverse configuration by providing a url or alias."
    examples = ["some_url", "some_alias"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "url_or_alias",
            help="The URL to the Dataverse server.",
            type=str,
            default=None,
            nargs="?",
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        raise NotImplementedError()

    @classmethod
    def run_command(cls, args):
        """Switch to an existing Dataverse configuration."""
        parser = cls.get_parser(argparse.ArgumentParser)
        dvn_conf = DVNConf(parser)
        dvn_conf.set_dvn(args.url_or_alias)
        show_available(dvn_conf)
