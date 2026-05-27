"""CLI create dataset."""
from pathlib import Path

from ibridges.cli.base import BaseCliCommand

from ibridgescontrib.ibridgesdvn.ds_meta import (
    build_metadata_json,
    gather_metadata_inputs,
)
from ibridgescontrib.ibridgesdvn.dvn_config import DVN_CONFIG_FP, DVNConf
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations
from ibridgescontrib.ibridgesdvn.utils import ensure_connection


class CliDvnCreateDataset(BaseCliCommand):
    """Command."""

    names = ["dv-create-ds"]
    description = "Create a new Dataverse dataset."

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument("dataverse_id", type=str)
        parser.add_argument(
            "--metajson",
            type=Path,
            help="Path to a JSON metadata file for dataset creation.",
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Command."""
        ops = DvnOperations()
        dvn_conf = DVNConf(DVN_CONFIG_FP, parser)

        cur_url = dvn_conf.cur_dvn

        exists, dvn_api, err = ensure_connection(dvn_conf, cur_url)
        if not exists:
            print(err)
            return

        if args.metajson:
            metadata_json = args.metajson.read_text(encoding="utf-8")

        else:
            print("Creating dataset interactively…")
            inputs = gather_metadata_inputs()
            metadata_json = build_metadata_json(inputs)

        response = dvn_api.create_dataset_from_json(
            args.dataverse_id,
            metadata_json,
        )

        pid = response["data"]["persistentId"].replace("doi:", "")
        ops.register_created_dataset(cur_url, pid)

        print(f"Dataset created with ID: {pid}")
