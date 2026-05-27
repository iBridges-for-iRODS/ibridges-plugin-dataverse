"""Dataverse GUI tab for iBridges."""

import logging
from pathlib import Path

import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets
from ibridges.session import Session
from ibridgesgui.config import get_last_ienv_path

from ibridgescontrib.ibridgesdvn.dvn_config import DVN_CONFIG_FP, DVNConf
from ibridgescontrib.ibridgesdvn.dvn_operations import DVN_OPS_PATH, TEMP_DIR, DvnOperations
from ibridgescontrib.ibridgesdvn.gui.dataset_table_controller import DatasetTableController
from ibridgescontrib.ibridgesdvn.gui.dataverse_connection_manager import DataverseConnectionManager
from ibridgescontrib.ibridgesdvn.gui.draft_manager import DraftManager
from ibridgescontrib.ibridgesdvn.gui.gui_popup_widgets import CreateDataset
from ibridgescontrib.ibridgesdvn.gui.gui_thread import TransferDataThread
from ibridgescontrib.ibridgesdvn.gui.irods_tree_controller import IrodsTreeController
from ibridgescontrib.ibridgesdvn.gui.push_workflow_manager import PushWorkflowManager
from ibridgescontrib.ibridgesdvn.gui.uiDataverse import Ui_Form


# pylint: disable=unnecessary-lambda
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
        self.irods_tree = None
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
        """Initialise gui elements."""
        # Dataverse connection manager
        self.dv_conn = DataverseConnectionManager(
            self.dvn_conf,
            self.dv_url_select_box,
            self.error_label,
        )

        self.draft_manager = DraftManager(
            self.draft_box,
            self.dvn_ops,
            self.error_label,
        )

        # Load Dataverse configurations into dropdown
        self.dv_conn.load_configurations()
        if self.dv_url_select_box.count() > 0:
            self.dv_url_select_box.setCurrentIndex(0)

        # When user selects a different Dataverse URL
        self.dv_url_select_box.currentIndexChanged.connect(self._on_dataverse_changed)

        # URL add/remove buttons
        self.add_url_button.clicked.connect(self.add_dv_url)
        self.delete_url_button.clicked.connect(self.delete_dv_url)

        # Dataset creation + selection
        self.draft_box.currentIndexChanged.connect(self._on_draft_selected)
        self.dv_create_ds_button.clicked.connect(self.dv_create_ds)

        # Dataverse file operations
        self.delete_selected_button.clicked.connect(self.dv_rm_file)
        self.dv_push_button.clicked.connect(self.dv_push)
        self.add_selected_button.clicked.connect(self.dv_add_file)
        self.add_selected_button.setEnabled(False)

        # iRODS tree
        self._init_irods_tree()

        # Dataset table controller
        self.dataset_table = DatasetTableController(
            self.selected_data_table,
            self.dv_ds_edit,
            self.error_label,
            self.dvn_api,
            self.dvn_ops,
            self.url,
            self.session,
            self.draft_manager.sync_dataset,
        )

        self.push_manager = PushWorkflowManager(
            dvn_api_getter=lambda: self.dvn_api,
            url_getter=lambda: self.url,
            dvn_conf=self.dvn_conf,
            dvn_ops=self.dvn_ops,
            temp_dir=self.temp_dir,
            get_dataset_id=lambda: self.dv_ds_edit.text().strip(),
            get_row_count=lambda: self.selected_data_table.rowCount(),
            create_transfer_thread=self._create_transfer_thread,
            update_table=self.dataset_table.populate_table,
            set_status=lambda msg: self.status_label.setText(msg),
            set_error=lambda msg: self.error_label.setText(msg),
            set_progress=self._set_progress,
            enable_gui=self._enable_buttons,
            clear_selection=lambda: self.irods_tree_view.clearSelection(),
            get_checksum_flag=lambda: self.check_checksum_box.isChecked(),
        )

        # When dataset ID is edited manually
        self.dv_ds_edit.textChanged.connect(self.dataset_edit_action)
        self._on_dataverse_changed()

    def add_dv_url(self):
        """Add a new dataverse configuration."""
        self.dv_conn.add_url()
        self.dv_conn.load_configurations()

    def delete_dv_url(self):
        """Remove a dataverse configuration."""
        self.dv_conn.delete_current()

    def dataset_edit_action(self):
        """Logic when new dataset id is entered in textfield."""
        self.add_selected_button.setEnabled(True)
        self.dataset_table.dataset_edit_action()

    def _on_dataverse_changed(self):
        self.dvn_api = self.dv_conn.connect_current()
        self.url = self.dv_conn.current_url
        if not self.dvn_api:
            self.dv_ds_edit.clear()
            self.draft_box.clear()
            return

        # refresh dataset table + drafts
        self.dataset_table.dvn_api = self.dvn_api
        self.dataset_table.url = self.dv_conn.current_url
        self.draft_manager.update_connection(self.dvn_api, self.url)
        self.draft_manager.load_drafts()
        self.draft_manager.select_first()

    def dv_create_ds(self):
        """Create a new dataset."""
        self.error_label.clear()

        if not self.dvn_api:
            self.error_label.setText("Not connected to Dataverse.")
            return

        widget = CreateDataset(self.dvn_api, self.dv_ds_edit)
        widget.exec()

        self.draft_manager.update_connection(self.dvn_api, self.url)
        self.draft_manager.load_drafts()
        self.draft_manager.select_first()

        doi = self.dv_ds_edit.text().strip()
        if doi:
            self.logger.info("DATAVERSE: Created Dataset %s", doi)

    # Stage file
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

        self.dataset_table.populate_table()
        self.irods_tree_view.clearSelection()
        self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.ArrowCursor))

    # Remove file from staging
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

        self.dataset_table.populate_table()

    # Push to dataverse
    def dv_push(self):
        """Upload staged files to dataset."""
        self.error_label.clear()
        self.push_manager.push()

    def _set_progress(self, value, maximum):
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)

    def _create_transfer_thread(self, url, token, dataset_id, checksum):
        return TransferDataThread(
            Path(get_last_ienv_path()),
            self.logger,
            self.dvn_ops,
            url,
            token,
            self.temp_dir,
            dataset_id,
            checksum,
        )

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

    def _on_draft_selected(self, _index):
        ds_id = self.draft_manager.get_selected_dataset_id()
        if not ds_id:
            return

        self.dv_ds_edit.setText(ds_id)
        self.add_selected_button.setEnabled(True)

    def _init_irods_tree(self):
        self.irods_tree = IrodsTreeController(self.session, self.irods_tree_view)
        self.irods_tree.init_tree()
        self.irods_model = self.irods_tree.model
