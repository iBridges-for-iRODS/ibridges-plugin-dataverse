"""Create the commands to interact with datasets."""

import ast
import shutil
import warnings
from pathlib import Path
from pprint import pprint

from ibridges import IrodsPath, download
from ibridges.cli.base import BaseCliCommand
from ibridges.cli.util import parse_remote

from ibridgescontrib.ibridgesdvn.dataverse import Dataverse
from ibridgescontrib.ibridgesdvn.ds_meta import build_metadata, gather_metadata_inputs
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations
from ibridgescontrib.ibridgesdvn.utils import calculate_checksum, create_unique_filename


class CliDvnCreateDataset(BaseCliCommand):
    """Subcommand to initialize ibridges."""

    names = ["dv-create-ds"]
    description = "Create a new dataset in a Dataverse collection."
    examples = ["dataverse_id --metajson file_path", "dataverse_id --metadata"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "dataverse_id",
            help="Identifier for the Dataverse where the new dataset will be created.",
            type=str,
        )

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--metajson",
            help="Metadata JSON file, e.g., like dataset.json from pyDataverse's user guide.",
            type=Path,
        )

        group.add_argument(
            "--metadata",
            help="Fetching the minimal metadata interactively and adding it to the dataset.",
            action="store_true",
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        # pylint: disable=R0912
        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn
        try:
            cur_token = dvn_conf.get_entry(cur_url)[1]["token"]
        except KeyError as err:
            raise KeyError(f"Please provide a token for {cur_url} through dvn-init.") from err
        dvn_api = Dataverse(cur_url, cur_token)

        if args.metajson and not args.metajson.is_file():
            parser.error(f"Cannot create dataset. {args.metajson} does not exist.")

        if not dvn_api.dataverse_exists(args.dataverse_id):
            parser.error(f"Cannot create dataset. Dataverse {args.dataverse_id} does not exist.")

        if args.metajson:
            dvn_api.create_dataset_with_json(args.dataverse_id, args.metajson)

        elif args.metadata:
            # Fetch info from user
            inputs = gather_metadata_inputs()
            metadata = build_metadata(inputs)
            pprint(metadata)
            dvn_api.create_dataset(args.dataverse_id, metadata)

    @classmethod
    def _cast(cls, my_list):
        if not my_list:
            return None
        try:
            return ast.literal_eval(my_list[0])
        except (ValueError, SyntaxError):
            return None

    @classmethod
    def _remove_prefix(cls, prefix, items):
        return [s.removeprefix(prefix + ":").strip() for s in items if s.startswith(prefix)]


class CliDvnAddFile(BaseCliCommand):
    """Subcommand to add (a) file(s) to a dataset."""

    names = ["dv-add-file"]
    description = "Mark one or more iRODS data objects to be uploaded to a Dataverse dataset."
    examples = ["dataset_name irods:path1 irods:path2"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "dataset",
            help="The name/id of the new dataset.",
            type=str,
            default=None,
        )
        parser.add_argument(
            "remote_path",
            help="Path to remote iRODS location starting with 'irods:'",
            type=str,
            nargs="+",
        )

        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        ops = DvnOperations()
        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn
        cur_token = dvn_conf.get_entry(cur_url)[1]["token"]
        dvn_api = Dataverse(cur_url, cur_token)
        if not dvn_api.dataset_exists(args.dataset):
            parser.error(f"Cannot mark data file, {args.dataset} does not exist.")

        for ipath in args.remote_path:
            irods_path = parse_remote(ipath, session)
            if not irods_path.exists():
                warnings.warn(f"{irods_path} does not exist, skip!")
                continue
            if irods_path.collection_exists():
                warnings.warn(f"{irods_path} is not a data object, skip!")
                continue
            if irods_path.size > 9 * 10**9:
                warnings.warn(
                        f"{irods_path} too large, size {irods_path.size} > {9 * 10**9}, skip!")
                continue

            ops.add_file(cur_url, args.dataset, str(irods_path))

        ops.show()


class CliDvnRmFile(BaseCliCommand):
    """Subcommand to add (a) file(s) to a dataset."""

    names = ["dv-rm-file"]
    description = "Remove one or more iRODS data objects from upload to a Dataverse dataset."
    examples = ["new_dataset_name irods:path1 irods:path2"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "dataset",
            help="The name/id of the new dataset.",
            type=str,
            default=None,
        )
        parser.add_argument(
            "remote_path",
            help="Path to remote iRODS location starting with 'irods:'",
            type=str,
            nargs="+",
        )

        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        ops = DvnOperations()
        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn

        for ipath in args.remote_path:
            irods_path = parse_remote(ipath, session)
            if not irods_path.exists():
                warnings.warn(f"{irods_path} does not exist, skip!")
                continue
            if irods_path.collection_exists():
                warnings.warn(f"{irods_path} is not a data object, skip!")
                continue
            ops.rm_file(cur_url, args.dataset, str(irods_path))


class CliDvnStatus(BaseCliCommand):
    """Summarise the changes to the dataset(s)."""

    names = ["dv-status"]
    description = "List all local changes to the dataset(s)."
    examples = [""]

    @staticmethod
    def run_shell(session, parser, args):
        """Print all stored dvn operations."""
        ops = DvnOperations()
        ops.show()


class CliDvnCleanUp(BaseCliCommand):
    """Clean up dvn operations where the list of irods paths is empty."""

    names = ["dv-cleanup"]
    description = "Cleanup all entries from the status, where the list of irods files is empty."
    examples = [""]

    @staticmethod
    def run_shell(session, parser, args):
        """Remove all unnecessary dvn operation entries."""
        ops = DvnOperations()
        ops.clean_up_datasets()
        ops.show()


class CliDvnPush(BaseCliCommand):
    """Push changes of a dataset to the currently configured Dataverse."""

    names = ["dv-push"]
    description = "Push all local changes to the dataverse collection."
    examples = ["dataset_id"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "dataset_id",
            help="The name/id of the dataset to send to dataverse.",
            type=str,
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--check-checksum",
            dest="check_checksum",
            action="store_true",
            help=(
                "Calculate the checksum for the data downloaded from iRODS and compare it "
                "with the checksum in Dataverse. To omit use --no-check-checksum."
            ),
        )
        group.add_argument(
            "--no-check-checksum",
            dest="check_checksum",
            action="store_false",
            help="Disable checksum checking.",
        )
        parser.set_defaults(check_checksum=True)
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        ops = DvnOperations()

        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn

        dvn_api = Dataverse(cur_url, dvn_conf.get_entry(cur_url)[1]["token"])

        if not dvn_api.dataset_exists(args.dataset_id):
            parser.error(f"{args.dataset_id} does not exist on {cur_url}")
            return

        # get objs under "add_file" for the dataset
        irods_paths = [IrodsPath(session, p) for p in ops.get_paths(cur_url, args.dataset_id)]

        temp_dir = Path.home() / ".dvn" / "data"
        temp_dir.mkdir(exist_ok=True)
        print("Data stored in ", temp_dir)

        for irods_path in irods_paths:
            if irods_path.dataobject_exists():
                try:
                    local_path = create_unique_filename(temp_dir, irods_path.name)
                    download(irods_path, local_path, overwrite=True)
                    print(f"Downloaded {irods_path} --> {local_path}")
                    dvn_api.add_datafile_to_dataset(args.dataset_id, local_path)
                    print(f"Uploaded {local_path} --> {args.dataset_id}")
                    if args.check_checksum:
                        alg, dvn_checksum = dvn_api.get_checksum_by_filename(
                            args.dataset_id, local_path.name
                        )
                        checksum = calculate_checksum(local_path, alg = alg)
                        if checksum != dvn_checksum:
                            warnings.warn(
                                "DATAVERSE ERROR: Local file and file in dataset are not the same."
                            )
                    ops.rm_file(cur_url, args.dataset_id, str(irods_path))
                    local_path.unlink()
                except Exception as err:  # pylint: disable=W0718
                    warnings.warn(f"Error in download and upload: {repr(err)}.")
                    raise err

            else:
                warnings.warn(f"{irods_path} does nor exist or is collection. Skip.")
        shutil.rmtree(temp_dir)
