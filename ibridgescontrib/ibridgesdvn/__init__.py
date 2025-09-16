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

SETUP_COMMANDS = [CliDvnAlias]
INIT_COMMANDS = [CliDvnInit]
SWITCH_COMMANDS = [CliDvnSwitch]
PUSH_COMMANDS = [CliDvnPush]
STATUS_COMMANDS = [CliDvnStatus]
CLEANUP_COMMANDS = [CliDvnCleanUp]
RM_FILE_COMMANDS = [CliDvnRmFile]
ADD_FILE_COMMANDS = [CliDvnAddFile]
CREATE_DS_COMMANDS = [CliDvnCreateDataset]

__all__ = ["get_dataverse_tab"]

def get_dataverse_tab():
    try:
        from ibridgescontrib.ibridgesdvn.gui.gui_dataverse import DataverseTab
    except ImportError as e:
        raise ImportError(
            "GUI dependencies missing. Install with:\n"
            "  pip install ibridgescontrib[gui]"
        ) from e
    return DataverseTab
