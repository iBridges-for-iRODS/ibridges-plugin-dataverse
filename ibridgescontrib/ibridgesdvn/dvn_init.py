import sys
import argparse
from getpass import getpass

from ibridges.cli.base import BaseCliCommand
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf


class CliDvnInit(BaseCliCommand):
    """Subcommand to initialize ibridges."""

    names = ["dvninit"]
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
        """Initialize ibridges by logging in."""
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
        print(dvn, entry)
        dvn_conf.save()
