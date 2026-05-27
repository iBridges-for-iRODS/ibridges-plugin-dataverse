"""Dataverse GUI tab for iBridges."""

import logging
import shutil
from pathlib import Path

import httpx
import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets
from ibridges import IrodsPath
from ibridges.session import Session
from ibridgesgui.config import get_last_ienv_path
from ibridgesgui.irods_tree_model import IrodsTreeModel

from ibridgescontrib.ibridgesdvn.dvn_config import DVN_CONFIG_FP, DVNConf
from ibridgescontrib.ibridgesdvn.dvn_operations import DVN_OPS_PATH, TEMP_DIR, DvnOperations
from ibridgescontrib.ibridgesdvn.gui.gui_popup_widgets import CreateDataset, CreateDvnURL
from ibridgescontrib.ibridgesdvn.gui.gui_thread import TransferDataThread
from ibridgescontrib.ibridgesdvn.gui.uiDataverse import Ui_Form
from ibridgescontrib.ibridgesdvn.utils import ensure_connection


class DataverseTab(PySide6.QtWidgets.QWidget, Ui_Form):
    """Dataverse tab for the iBridges GUI."""

    name = "Dataverse"

    def __init__(self, session: Session, app_name: str, logger: logging.Logger):
        """Init."""
        super().__init__()
        super().setupUi(self)

        self.logger = logger
        self.logger.setLevel(logging.INFO)
        self.session = session
        self.app_name = app_name

        # Configuration
        self.dvn_conf = DVNConf(DVN_CONFIG_FP)
        self.dvn_ops = DvnOperations(DVN_OPS_PATH)
        self.temp_dir = TEMP_DIR
        self.dvn_api = None

        # GUI state
        self.url = None
        self.irods_model = None
        self.transfer_thread = None

        self.error_label.setWordWrap(True)

        header = self.selected_data_table.horizontalHeader()
        header.setSectionResizeMode(0, PySide6.QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, PySide6.QtWidgets.QHeaderView.ResizeToContents)
        self.selected_data_table.setSizePolicy(
            PySide6.QtWidgets.QSizePolicy.Expanding, PySide6.QtWidgets.QSizePolicy.Expanding
        )

        self.init_tab()

    def init_tab(self):
        """Initialise gui elelemnts."""
        self.load_dataverse_conf()
        self.dv_url_select_box.currentTextChanged.connect(self._connect_to_dataverse)

        self.add_url_button.clicked.connect(self.add_dv_url)
        self.delete_url_button.clicked.connect(self.delete_dv_url)

        self.draft_box.currentIndexChanged.connect(self._on_draft_selected)
        self.dv_ds_edit.textChanged.connect(self.dataset_edit_action)
        self.dv_create_ds_button.clicked.connect(self.dv_create_ds)

        self.delete_selected_button.clicked.connect(self.dv_rm_file)
        self.dv_push_button.clicked.connect(self.dv_push)
        self.add_selected_button.clicked.connect(self.dv_add_file)
        self.add_selected_button.setEnabled(False)

        self._init_irods_tree()
        self._connect_to_dataverse()
        self.load_drafts_into_box()

    def load_dataverse_conf(self):
        """Load Dataverse configurations with validation (same logic as CLI)."""
        self.dv_url_select_box.clear()

        items = []

        for url, entry in self.dvn_conf.dvns.items():
            alias = entry.get("alias")
            alias_display = alias if alias else "[no alias]"
            token = entry.get("token")

            # --- URL validation ---
            try:
                resp = httpx.get(f"{url}/api/info/version", timeout=3.0)
                if resp.status_code == 200:
                    url_status = "dataverse OK"
                else:
                    url_status = "invalid dataverse"
            except Exception:
                url_status = "unreachable"

            # --- Token validation ---
            if token and url_status == "dataverse OK":
                try:
                    resp = httpx.get(
                        f"{url}/api/users/:me",
                        headers={"X-Dataverse-key": token},
                        timeout=3.0,
                    )
                    token_status = "token OK" if resp.status_code == 200 else "token invalid"
                except Exception:
                    token_status = "token invalid"
            else:
                token_status = "no token" if not token else "token invalid"

            # --- Build display label (NO marker) ---
            label = f"{alias_display}  →  {url}  [{url_status}, {token_status}]"

            items.append((label, url))

        # Populate dropdown
        for label, url in items:
            self.dv_url_select_box.addItem(label, userData=url)

        # Auto-select the current Dataverse
        if self.dvn_conf.cur_dvn:
            for i in range(self.dv_url_select_box.count()):
                if self.dv_url_select_box.itemData(i) == self.dvn_conf.cur_dvn:
                    self.dv_url_select_box.setCurrentIndex(i)
                    break

    def _connect_to_dataverse(self):
        """Connect GUI to Dataverse using the stored URL (not the label)."""
        self.error_label.clear()

        self.url = self.dv_url_select_box.currentData()

        if not self.url:
            self.error_label.setText("Please create a Dataverse configuration.")
            return

        # test dataverse connection with url and stored token
        state, dvn_api, error = ensure_connection(self.dvn_conf, self.url)

        if error:
            self.error_label.setText(f"Invalid Dataverse connection: {error}")
            return

        # store last used params
        self.dvn_api = dvn_api
        self.dvn_conf.set_dvn(self.url)

        # clear possible clutter in ds field
        self.dv_ds_edit.clear()

    def add_dv_url(self):
        """Add new dvn configuration."""
        self.error_label.clear()
        url_widget = CreateDvnURL(self.dvn_conf)
        url_widget.exec()
        self.load_dataverse_conf()

    def delete_dv_url(self):
        """Remove a Dataverse configuration."""
        # Get the actual URL stored in userData
        cur_url = self.dv_url_select_box.currentData()

        if not cur_url:
            self.error_label.setText("No Dataverse selected.")
            return
        try:
            self.dvn_conf.delete_alias(cur_url)
        except KeyError as exc:
            self.logger.info("DATAVERSE: %s", exc)
        self.load_dataverse_conf()

    def load_drafts_into_box(self):
        
        self.draft_box.clear()
        if not self.dvn_api:
            return
    
        drafts = self.dvn_ops.get_created_datasets(self.url)
    
        for ds in drafts:
            try:
                state = self.dvn_api.get_dataset_state(ds)
            except Exception:
                state = "UNKNOWN"
    
            # Display text, store dataset ID as userData
            display = f"{ds} [{state}]"
            self.draft_box.addItem(display, userData=ds)


    def _on_draft_selected(self, index):
        if index < 0:
            return

        ds_id = self.draft_box.itemData(index)
        if not ds_id:
            return

        # Pass the dataset ID to dv_ds_edit
        self.dv_ds_edit.setText(ds_id)
        #self.dataset_edit_action()

    def _sync_draft_box(self, dataset_id):
        """Ensure draft_box reflects the currently loaded dataset ID."""
    
        # First check if dataset_id is already in the combobox
        found_index = -1
        for i in range(self.draft_box.count()):
            if self.draft_box.itemData(i) == dataset_id:
                found_index = i
                break
    
        if found_index >= 0:
            # Dataset already exists → switch to it
            self.draft_box.setCurrentIndex(found_index)
            return
    
        # Otherwise create a new entry
        # Try to fetch state (optional but nice)
        try:
            state = self.dvn_api.get_dataset_state(dataset_id)
            self.dvn_ops.register_created_dataset(self.dvn_api.url, dataset_id)
        except Exception:
            state = "UNKNOWN"
    
        display = f"{dataset_id} [{state}]"
        self.draft_box.addItem(display, userData=dataset_id)
    
        # Switch to the newly added entry
        self.draft_box.setCurrentIndex(self.draft_box.count() - 1)


    def dv_create_ds(self):
        """Create a new dataset."""
        self.error_label.clear()

        if not self.dvn_api:
            self.error_label.setText("Not connected to Dataverse.")
            return

        widget = CreateDataset(self.dvn_api, self.dv_ds_edit)
        widget.exec()

        self.load_drafts_into_box()
        doi = self.dv_ds_edit.text().strip()
        if doi:
            self.logger.info("DATAVERSE: Created Dataset %s", doi)

    # ------------------------------------------------------------------
    # FILE REMOVAL
    # ------------------------------------------------------------------

    def dv_rm_file(self):
        """Unstage a file."""
        self.error_label.clear()
        dataset_id = self.dv_ds_edit.text().strip()

        if not self.dvn_api:
            self.error_label.setText("Not connected to Dataverse.")
            return

        if not dataset_id or not self.dvn_api.dataset_exists(dataset_id):
            self.error_label.setText("Enter a valid Dataset Identifier.")
            return

        rows = {idx.row() for idx in self.selected_data_table.selectedIndexes()}
        for row in rows:
            path = self.selected_data_table.item(row, 0).text()
            self.dvn_ops.rm_file(self.url, dataset_id, path)

        self._populate_selected_data_table()

    # ------------------------------------------------------------------
    # PUSH WORKFLOW
    # ------------------------------------------------------------------

    def dv_push(self):
        """Upload staged files to dataset."""
        self.error_label.clear()
        dataset_id = self.dv_ds_edit.text().strip()

        if not self.dvn_api:
            self.error_label.setText("Not connected to Dataverse.")
            return
        if not dataset_id or not self.dvn_api.dataset_exists(dataset_id):
            self.error_label.setText("Enter a valid Dataset Identifier.")
            return

        if self.selected_data_table.rowCount() == 0:
            self.error_label.setText("Please add some data from the iRODS tree.")
            return

        self.temp_dir.mkdir(exist_ok=True)
        token = self.dvn_conf.get_token(self.url)

        try:
            self.transfer_thread = TransferDataThread(
                Path(get_last_ienv_path()),
                self.logger,
                self.dvn_ops,
                self.url,
                token,
                self.temp_dir,
                dataset_id,
                self.check_checksum_box.isChecked(),
            )
        except Exception as err:
            msg = f"Could not instantiate a new session: {repr(err)}"
            self.error_label.setText(msg)
            self.logger.error("DATAVERSE: %s", msg)
            return

        self.transfer_thread.current_progress.connect(self._transfer_status)
        self.transfer_thread.result.connect(self._transfer_end)
        self.transfer_thread.finished.connect(self._finish_transfer_data)

        self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.WaitCursor))
        self._enable_buttons(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(self.selected_data_table.rowCount())
        self.transfer_thread.start()

    def _enable_buttons(self, enable: bool):
        self.add_selected_button.setEnabled(enable)
        self.check_checksum_box.setEnabled(enable)
        self.delete_selected_button.setEnabled(enable)
        self.dv_ds_edit.setEnabled(enable)
        self.dv_create_ds_button.setEnabled(enable)
        self.dv_push_button.setEnabled(enable)
        self.selected_data_table.setEnabled(enable)
        self.dv_url_select_box.setEnabled(enable)
        self.add_url_button.setEnabled(enable)
        self.delete_url_button.setEnabled(enable)
        self.irods_tree_view.setEnabled(enable)

    def _transfer_status(self, state: list):
        obj_count, num_objs, obj_failed = state
        self.progress_bar.setValue(obj_count)
        self.status_label.setText(f"{obj_count} of {num_objs} files; failed: {obj_failed}.")

    def _transfer_end(self, thread_output: dict):
        if thread_output["error"]:
            self.error_label.setText(thread_output["error"])
            self._populate_selected_data_table()
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            return

        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self._populate_selected_data_table()
        self.status_label.clear()
        self.error_label.setText("Transfer finished, visit Dataverse to publish.")
        self._enable_buttons(True)

    def _finish_transfer_data(self):
        self._enable_buttons(True)
        self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.ArrowCursor))
        if self.transfer_thread:
            del self.transfer_thread

    # ------------------------------------------------------------------
    # ADD FILE
    # ------------------------------------------------------------------

    def dv_add_file(self):
        """Stage files."""
        self.error_label.clear()

        if not self.dvn_api:
            self.error_label.setText("Not connected to Dataverse.")
            return

        irods_selection = self.irods_tree_view.selectedIndexes()
        if not irods_selection:
            self.error_label.setText("Please select a data object.")
            return

        dataset_id = self.dv_ds_edit.text().strip()
        if not dataset_id or not self.dvn_api.dataset_exists(dataset_id):
            self.error_label.setText("Enter a valid Dataset Identifier.")
            return

        self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.WaitCursor))

        for idx in irods_selection:
            irods_path = self.irods_model.irods_path_from_tree_index(idx)
            if irods_path.dataobject_exists():
                if irods_path.size > 9 * 10**9:
                    self.error_label.setText(
                        f"{irods_path} too large: size {irods_path.size} > {9 * 10**9}"
                    )
                else:
                    self.dvn_ops.add_file(self.url, dataset_id, str(irods_path))
            else:
                self.error_label.setText("Please only select data objects.")

        self._populate_selected_data_table()
        self.irods_tree_view.clearSelection()
        self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.ArrowCursor))

    # ------------------------------------------------------------------
    # IRODS TREE
    # ------------------------------------------------------------------

    def _irods_root(self):
        lowest = IrodsPath(self.session).absolute()
        while lowest.parent.exists() and str(lowest) != "/":
            lowest = lowest.parent
        return lowest

    def _init_irods_tree(self):
        root = self._irods_root()
        self.irods_model = IrodsTreeModel(self.irods_tree_view, root)
        self.irods_tree_view.setModel(self.irods_model)
        self.irods_tree_view.expanded.connect(self.irods_model.refresh_subtree)
        self.irods_model.init_tree()
        self.irods_tree_view.expand(self.irods_model.index(0, 0))

        # hide unnecessary columns
        for col in range(1, 6):
            self.irods_tree_view.setColumnHidden(col, True)

    # ------------------------------------------------------------------
    # DATASET TABLE
    # ------------------------------------------------------------------

    def dataset_edit_action(self):
        """Update dataset info in table."""
        self.error_label.clear()
        self._enable_buttons(True)
        self._populate_selected_data_table()

    def _populate_selected_data_table(self):
        self.add_selected_button.setEnabled(True)
        self.selected_data_table.setRowCount(0)

        dataset_id = self.dv_ds_edit.text().strip()
        if not dataset_id:
            self.error_label.setText("Enter a valid Dataset Identifier.")
            return
        if not self.dvn_api:
            self.error_label.setText(
                "Not connected to Dataverse. Check Dataverse URL and Configuration."
            )
            return
        if not self.dvn_api.dataset_exists(dataset_id):
            self.error_label.setText("Dataset does not exist (any longer).")
            return
        
        self._sync_draft_box(dataset_id)

        paths = self.dvn_ops.get_paths(self.url, dataset_id)
        if not paths:
            return

        try:
            current_paths = [
                (IrodsPath(self.session, path), IrodsPath(self.session, path).size)
                for path in paths
            ]
        except FileNotFoundError as err:
            self.error_label.setText(f"Cannot load staged file: {err}")
            self.add_selected_button.setEnabled(False)
            self.check_checksum_box.setEnabled(False)
            self.delete_selected_button.setEnabled(False)
            self.dv_push_button.setEnabled(False)
            return

        self.selected_data_table.clearContents()
        self.selected_data_table.setRowCount(len(current_paths))

        for row, (irods_path, size) in enumerate(current_paths):
            # Column 0: full path (long single word)
            item_path = PySide6.QtWidgets.QTableWidgetItem(str(irods_path))
            item_path.setToolTip(str(irods_path))
            self.selected_data_table.setItem(row, 0, item_path)

            # Column 1: file size
            item_size = PySide6.QtWidgets.QTableWidgetItem(str(size))
            # item_size.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.selected_data_table.setItem(row, 1, item_size)
