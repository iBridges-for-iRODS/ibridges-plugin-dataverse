import sys
from ibridges.cli.base import BaseCliCommand
from dvn_config import DVNConf


class CliDvnInit(BaseCliCommand):
    """Subcommand to initialize ibridges."""

    names = ["init"]
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
        dvn_conf.set_env(url_or_alias)
        dvn, entry = DVNConf(parser).get_entry()
        
        
        if sys.stdin.isatty() or "ipykernel" in sys.modules:
            token = getpass("Your Dataverse token for {url_or_alias} : ")
        else:
            print("Your Dataverse token for {url_or_alias} : ")
            token = sys.stdin.readline().rstrip()
        
        entry["token"] = token
        dvn_conf.save()
