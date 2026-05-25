from pathlib import Path
import json
import ast

from ibridges.cli.base import BaseCliCommand
from ibridgescontrib.ibridgesdvn.dataverse import Dataverse
from ibridgescontrib.ibridgesdvn.ds_meta import build_metadata, gather_metadata_inputs
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations


class CliDvnCreateDataset(BaseCliCommand):
    names = ["dv-create-ds"]
    description = "Create a new dataset in a Dataverse collection."
    examples = ["dataverse_id --metajson file_path", "dataverse_id --metadata"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument("dataverse_id", type=str)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--metajson", type=Path)
        group.add_argument("--metadata", action="store_true")
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn
        token = dvn_conf.get_entry(cur_url)[1]["token"]

        dvn_api = Dataverse(cur_url, token)
        ops = DvnOperations()

        if args.metajson and not args.metajson.is_file():
            parser.error(f"{args.metajson} does not exist.")

        if not dvn_api.dataverse_exists(args.dataverse_id):
            parser.error(f"Dataverse {args.dataverse_id} does not exist.")

        if args.metajson:
            response = dvn_api.create_dataset_with_json(args.dataverse_id, args.metajson)
        else:
            inputs = gather_metadata_inputs()
            metadata_dict = build_metadata(inputs)
            metadata_json = json.dumps(metadata_dict, indent=2)
            response = dvn_api.create_dataset(args.dataverse_id, metadata_json)

        dataset_id = response["data"]["persistentId"].removeprefix("doi:")
        ops.register_created_dataset(cur_url, dataset_id)

        print(f"Created dataset {dataset_id} in {args.dataverse_id}")
