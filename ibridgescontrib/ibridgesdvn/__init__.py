"""Create links to python classes."""

from ibridgescontrib.ibridgesdvn.dvn_dataset_commands import (
    CliDvnAddDatasetMeta,
    CliDvnAddFile,
    CliDvnCreateDataset,
    CliDvnPush,
    CliDvnRmFile,
    CliDvnStatus,
)
from ibridgescontrib.ibridgesdvn.dvn_init import CliDvnInit, CliDvnSwitch
from ibridgescontrib.ibridgesdvn.dvn_setup import CliDvnAlias
from ibridgescontrib.ibridgesdvn.gui_dataverse import DataverseTab

SETUP_COMMANDS = [CliDvnAlias]
INIT_COMMANDS = [CliDvnInit]
SWITCH_COMMANDS = [CliDvnSwitch]
PUSH_COMMANDS = [CliDvnPush]
STATUS_COMMANDS = [CliDvnStatus]
RM_FILE_COMMANDS = [CliDvnRmFile]
ADD_FILE_COMMANDS = [CliDvnAddFile]
META_DS_COMMANDS = [CliDvnAddDatasetMeta]
CREATE_DS_COMMANDS = [CliDvnCreateDataset]

__all__ = ["DataverseTab"]
