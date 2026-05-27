"""Create links to python classes."""

# Dataset‑related commands (now split into separate files)
from ibridgescontrib.ibridgesdvn.cli.dscommands.dv_add_file import CliDvnAddFile
from ibridgescontrib.ibridgesdvn.cli.dscommands.dv_cleanup import CliDvnCleanUp
from ibridgescontrib.ibridgesdvn.cli.dscommands.dv_create_ds import CliDvnCreateDataset
from ibridgescontrib.ibridgesdvn.cli.dscommands.dv_drafts import CliDvnDrafts
from ibridgescontrib.ibridgesdvn.cli.dscommands.dv_push import CliDvnPush
from ibridgescontrib.ibridgesdvn.cli.dscommands.dv_rm_file import CliDvnRmFile
from ibridgescontrib.ibridgesdvn.cli.dscommands.dv_status import CliDvnStatus

# Setup / init commands
from ibridgescontrib.ibridgesdvn.cli.dvn_init import CliDvnInit, CliDvnSwitch
from ibridgescontrib.ibridgesdvn.cli.dvn_setup import CliDvnAlias

# Command groups used by the CLI framework
SETUP_COMMANDS = [CliDvnAlias]
INIT_COMMANDS = [CliDvnInit]
SWITCH_COMMANDS = [CliDvnSwitch]

CREATE_DS_COMMANDS = [CliDvnCreateDataset]
ADD_FILE_COMMANDS = [CliDvnAddFile]
RM_FILE_COMMANDS = [CliDvnRmFile]
CLEANUP_COMMANDS = [CliDvnCleanUp]
STATUS_COMMANDS = [CliDvnStatus]
PUSH_COMMANDS = [CliDvnPush]
DRAFT_COMMANDS = [CliDvnDrafts]

__all__ = ["get_dataverse_tab"]


# pylint: disable=import-outside-toplevel
def get_dataverse_tab():
    """Import for GUI."""
    try:
        from ibridgescontrib.ibridgesdvn.gui.gui_dataverse import DataverseTab
    except ImportError as e:
        raise ImportError(
            "GUI dependencies missing. Install with:\n  pip install ibridgescontrib[gui]"
        ) from e
    return DataverseTab
