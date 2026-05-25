from ibridges.cli.base import BaseCliCommand

from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations


class CliDvnCleanUp(BaseCliCommand):
    names = ["dv-cleanup"]
    description = "Remove empty dataset entries from the operations log."

    @staticmethod
    def run_shell(session, parser, args):
        ops = DvnOperations()
        ops.clean_up_datasets()
        ops.show()
