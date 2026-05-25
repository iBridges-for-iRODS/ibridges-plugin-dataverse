import warnings
from ibridges import IrodsPath
from ibridges.cli.base import BaseCliCommand
from ibridges.cli.util import parse_remote

from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf
from ibridgescontrib.ibridgesdvn.dataverse import Dataverse


class CliDvnAddFile(BaseCliCommand):
    names = ["dv-add-file"]
    description = "Stage iRODS files for upload to a Dataverse dataset."

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
        token = dvn_conf.get_entry(cur_url)[1]["token"]

        dvn_api = Dataverse(cur_url, token)

        if not dvn_api.dataset_exists(args.dataset):
            parser.error(f"Dataset {args.dataset} does not exist.")

        # Register dataset as a draft if not already tracked
        if args.dataset not in ops.get_created_datasets(cur_url):
            ops.register_created_dataset(cur_url, args.dataset)

        for ipath in args.remote_path:
            irods_path = parse_remote(ipath, session)

            if not irods_path.exists():
                warnings.warn(f"{irods_path} does not exist.")
                continue
            if irods_path.collection_exists():
                warnings.warn(f"{irods_path} is a collection, skipping.")
                continue
            if irods_path.size > 9 * 10**9:
                warnings.warn(f"{irods_path} too large (>9GB), skipping.")
                continue

            ops.add_file(cur_url, args.dataset, str(irods_path))

        ops.show(dvn_api)
