"""Managing draft datasets."""

from ibridges.cli.base import BaseCliCommand
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf
from ibridgescontrib.ibridgesdvn.dataverse import Dataverse


class CliDvnDrafts(BaseCliCommand):
    """List or delete draft datasets."""

    names = ["dv-draft"]
    description = "List or delete draft datasets created locally."
    examples = ["", "--delete doi:12345"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "-d", "--delete",
            nargs="+",
            help="Delete one or more draft dataset IDs locally."
        )
        
        parser.add_argument(
            "-D", "--force-delete",
            nargs="+",
            help="Force delete datasets locally and from Dataverse."
        )

        return parser

    @staticmethod
    def run_shell(session, parser, args):
        ops = DvnOperations()
        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn
        token = dvn_conf.get_entry(cur_url)[1]["token"]
        dvn_api = Dataverse(cur_url, token)

        if args.force_delete:
            for ds in args.force_delete:
                ops.force_delete_dataset(cur_url, ds, dvn_api)
            ops.show_created_datasets(dvn_api=dvn_api)
            return
        
        if args.delete:
            for ds in args.delete:
                ops.delete_created_datasets(cur_url, [ds])
            ops.show_created_datasets(dvn_api=dvn_api)
            return

        dataset_ids = ops.get_created_datasets(cur_url)

        if not dataset_ids:
            print("No draft datasets tracked locally.")
            return

        ops.show_created_datasets(dvn_api=dvn_api)
