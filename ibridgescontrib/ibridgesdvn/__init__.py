"""Create links to python classes."""

from ibridgescontrib.ibridgesdvn.dvn_dataset_commands import (
    CliDvnAddFile,
    CliDvnCleanUp,
    CliDvnCreateDataset,
    CliDvnPush,
    CliDvnRmFile,
    CliDvnStatus,
)
from ibridgescontrib.ibridgesdvn.dvn_init import CliDvnInit, CliDvnSwitch
from ibridgescontrib.ibridgesdvn.dvn_setup import CliDvnAlias
from ibridgescontrib.ibridgesdvn.gui_dataverse import DataverseTab
from ibridgescontrib.ibridgesdvn.gui_thread import TransferDataThread

SETUP_COMMANDS = [CliDvnAlias]
INIT_COMMANDS = [CliDvnInit]
SWITCH_COMMANDS = [CliDvnSwitch]
PUSH_COMMANDS = [CliDvnPush]
STATUS_COMMANDS = [CliDvnStatus]
CLEANUP_COMMANDS = [CliDvnCleanUp]
RM_FILE_COMMANDS = [CliDvnRmFile]
ADD_FILE_COMMANDS = [CliDvnAddFile]
CREATE_DS_COMMANDS = [CliDvnCreateDataset]


__all__ = ["DataverseTab"]
