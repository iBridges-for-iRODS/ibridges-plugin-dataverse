import shutil
import warnings
from pathlib import Path

from ibridges import IrodsPath, download
from ibridges.cli.base import BaseCliCommand

from ibridgescontrib.ibridgesdvn.utils import calculate_checksum, create_unique_filename
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf
from ibridgescontrib.ibridgesdvn.dataverse import Dataverse


class CliDvnPush(BaseCliCommand):
    names = ["dv-push"]
    description = "Upload staged files to Dataverse."

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument("dataset_id", type=str)
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--check-checksum", action="store_true")
        group.add_argument("--no-check-checksum", dest="check_checksum", action="store_false")
        parser.set_defaults(check_checksum=True)
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        ops = DvnOperations()
        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn
        token = dvn_conf.get_entry(cur_url)[1]["token"]

        dvn_api = Dataverse(cur_url, token)

        if not dvn_api.dataset_exists(args.dataset_id):
            parser.error(f"{args.dataset_id} does not exist.")

        irods_paths = ops.get_paths(cur_url, args.dataset_id)
        if not irods_paths:
            print("No files staged for upload.")
            return

        temp_dir = Path.home() / ".dvn" / "data"
        temp_dir.mkdir(exist_ok=True)

        for p in irods_paths:
            ipath = IrodsPath(session, p)

            if not ipath.dataobject_exists():
                warnings.warn(f"{ipath} does not exist.")
                continue

            try:
                local_path = create_unique_filename(temp_dir, ipath.name)
                download(ipath, local_path, overwrite=True)

                dvn_api.add_datafile_to_dataset(args.dataset_id, local_path)

                if args.check_checksum:
                    alg, dvn_checksum = dvn_api.get_checksum_by_filename(
                        args.dataset_id, local_path.name
                    )
                    checksum = calculate_checksum(local_path, alg=alg)
                    if checksum != dvn_checksum:
                        warnings.warn("Checksum mismatch.")

                ops.rm_file(cur_url, args.dataset_id, p)
                local_path.unlink()

            except Exception as err:
                warnings.warn(f"Error: {repr(err)}")
                raise err

        shutil.rmtree(temp_dir)

        ops.flush_dataset(cur_url, args.dataset_id)

        if dvn_api.is_dataset_published(args.dataset_id):
            ops.delete_created_datasets(cur_url, [args.dataset_id])
