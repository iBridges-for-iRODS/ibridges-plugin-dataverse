import warnings
from ibridges import IrodsPath
from ibridges.cli.base import BaseCliCommand
from ibridges.cli.util import parse_remote

from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf


class CliDvnRmFile(BaseCliCommand):
    names = ["dv-rm-file"]
    description = "Unstage iRODS files from a Dataverse dataset."

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument("dataset", type=str)
        parser.add_argument("remote_path", nargs="+", type=str)
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        ops = DvnOperations()
        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn

        for ipath in args.remote_path:
            irods_path = parse_remote(ipath, session)

            if not irods_path.exists():
                warnings.warn(f"{irods_path} does not exist.")
                continue
            if irods_path.collection_exists():
                warnings.warn(f"{irods_path} is a collection.")
                continue

            ops.rm_file(cur_url, args.dataset, str(irods_path))

        ops.show()

