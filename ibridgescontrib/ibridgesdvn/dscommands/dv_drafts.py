from ibridges.cli.base import BaseCliCommand

from ibridgescontrib.ibridgesdvn.dataverse import Dataverse
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations


class CliDvnDrafts(BaseCliCommand):
    names = ["dv-draft"]
    description = "Show draft datasets and optionally delete them."

    @classmethod
    def _mod_parser(cls, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "-d",
            "--delete-local",
            nargs="+",
            metavar="DATASET_ID",
            help="Delete the given draft dataset IDs locally only.",
        )
        group.add_argument(
            "-D",
            "--delete-remote",
            nargs="+",
            metavar="DATASET_ID",
            help="Delete the given draft dataset IDs locally and on Dataverse.",
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        ops = DvnOperations()
        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn
        token = dvn_conf.get_entry(cur_url)[1]["token"]
        api = Dataverse(cur_url, token)

        drafts = ops.get_created_datasets(cur_url)

        # Always show current drafts
        print("Draft datasets:")
        if drafts:
            for ds in drafts:
                try:
                    state = api.get_dataset_state(ds)
                except Exception:
                    state = "UNKNOWN"
                print(f"  • {ds} [{state}]")
        else:
            print("  (none)")

        # No deletion flags → just listing
        if not args.delete_local and not args.delete_remote:
            return

        # Determine which IDs the user wants to delete
        if args.delete_local:
            to_delete = args.delete_local
            delete_remote = False
        else:
            to_delete = args.delete_remote
            delete_remote = True

        # Filter to IDs that are actually tracked as drafts
        existing_drafts = set(drafts)
        selected = [ds for ds in to_delete if ds in existing_drafts]

        if not selected:
            print("No matching draft dataset IDs to delete.")
            return

        if delete_remote:
            for ds in selected:
                try:
                    api.delete_dataset(ds)
                    print(f"Deleted dataset {ds} on Dataverse.")
                except Exception as err:
                    print(f"Failed to delete {ds} on Dataverse: {err}")

        ops.delete_created_datasets(cur_url, selected)
        print("Locally removed draft entries:", ", ".join(selected))
