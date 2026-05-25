from ibridges.cli.base import BaseCliCommand

from ibridgescontrib.ibridgesdvn.dataverse import Dataverse
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations


class CliDvnStatus(BaseCliCommand):
    names = ["dv-status"]
    description = "Show pending uploads and draft datasets."

    @staticmethod
    def run_shell(session, parser, args):
        ops = DvnOperations()
        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn
        token = dvn_conf.get_entry(cur_url)[1]["token"]

        dvn_api = Dataverse(cur_url, token)

        # Clean up published drafts (optional but recommended)
        ops.remove_published_drafts(cur_url, dvn_api)

        # Unified status display
        ops.show_status(cur_url, dvn_api)
