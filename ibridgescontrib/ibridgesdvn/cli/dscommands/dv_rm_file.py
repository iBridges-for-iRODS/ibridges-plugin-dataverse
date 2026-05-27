"""Command to unstage files."""

from ibridges.cli.base import BaseCliCommand

from ibridgescontrib.ibridgesdvn.dvn_config import DVN_CONFIG_FP, DVNConf
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations


class CliDvnRmFile(BaseCliCommand):
    """Unstage file."""

    names = ["dv-rm-file"]
    description = "Remove a staged file from the Dataverse upload queue."

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument("dataset_id", type=str)
        parser.add_argument("irods_path", type=str)
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Command."""
        dvn_conf = DVNConf(DVN_CONFIG_FP, parser)
        cur_url = dvn_conf.cur_dvn

        ops = DvnOperations()
        ops.rm_file(cur_url, args.dataset_id, args.irods_path)

        print(f"Removed staged file {args.irods_path} from dataset {args.dataset_id}.")
