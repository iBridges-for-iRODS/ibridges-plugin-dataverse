from pathlib import Path
from ibridges.cli.base import BaseCliCommand

from ibridgescontrib.ibridgesdvn.dataverse import Dataverse
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations

from ibridgescontrib.ibridgesdvn.ds_meta import (
    gather_metadata_inputs,
    build_metadata_json,
)


class CliDvnCreateDataset(BaseCliCommand):
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
        ops = DvnOperations()
        dvn_conf = DVNConf(parser)

        cur_url = dvn_conf.cur_dvn
        token = dvn_conf.get_entry(cur_url)[1]["token"]

        dvn_api = Dataverse(cur_url, token)

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
