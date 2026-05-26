"""CLI clean up cache."""
from ibridges.cli.base import BaseCliCommand

from ibridgescontrib.ibridgesdvn.dvn_config import DVN_CONFIG_FP, DVNConf
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations


class CliDvnCleanUp(BaseCliCommand):
    """Command."""

    names = ["dv-cleanup"]
    description = "Clean up local Dataverse operation logs."

    @staticmethod
    def run_shell(session, parser, args):
        """CLI."""
        # Load config to know which DVN is active
        dvn_conf = DVNConf(DVN_CONFIG_FP, parser)
        dv_url = dvn_conf.cur_dvn

        if not dv_url:
            raise RuntimeError("No active Dataverse selected. Use 'dv-setup' first.")

        ops = DvnOperations()

        # Manual cleanup (wrapper)
        ops.clean_up_datasets(dv_url, parser)

        # Show status after cleanup
        api = ops._get_api(dv_url, parser)
        ops.show_status(dv_url, api)
