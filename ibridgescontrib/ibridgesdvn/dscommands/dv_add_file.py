import warnings

from ibridges.cli.base import BaseCliCommand
from ibridges.cli.util import parse_remote

from ibridgescontrib.ibridgesdvn.dataverse import Dataverse
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations


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

            # Validate existence
            if not irods_path.exists():
                warnings.warn(f"{irods_path} does not exist.")
                continue

            # Skip collections
            if irods_path.collection_exists():
                warnings.warn(f"{irods_path} is a collection, skipping.")
                continue

            # Check size using Dataverse max upload size
            try:
                irods_size = irods_path.size
            except Exception:
                irods_size = 0

            max_size = dvn_api.get_max_upload_size()
            if max_size > 0 and irods_size > max_size:
                warnings.warn(
                    f"{irods_path} too large ({irods_size} bytes > {max_size} bytes), skipping."
                )
                continue

            # Stage file
            ops.add_file(cur_url, args.dataset, str(irods_path))

        ops.show_status(cur_url, dvn_api)

