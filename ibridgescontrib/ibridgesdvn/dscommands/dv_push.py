from ibridges.cli.base import BaseCliCommand
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf


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
        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn

        ops = DvnOperations()
        ops.push_dataset(
            session=session,
            dv_url=cur_url,
            dataset_id=args.dataset_id,
            check_checksum=args.check_checksum,
        )
