"""Example tab class to extend the iBridgesGUI app."""

import logging
import shutil
from pathlib import Path

import PySide6.QtWidgets
from ibridges import IrodsPath, download
from ibridges.session import Session
from ibridgesgui.gui_utils import populate_table
from ibridgesgui.irods_tree_model import IrodsTreeModel

from ibridgescontrib.ibridgesdvn.dataverse import Dataverse
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations
from ibridgescontrib.ibridgesdvn.gui_popup_widgets import CreateDataset, CreateDvnURL
from ibridgescontrib.ibridgesdvn.uiDataverse import Ui_Form
from ibridgescontrib.ibridgesdvn.utils import create_unique_filename

# pylint: disable=R0902


class DataverseTab(PySide6.QtWidgets.QWidget, Ui_Form):
    """Example tab for the iBridges GUI."""

    name = "Dataverse"

    def __init__(self, session: Session, app_name: str, logger: logging.Logger):
        """Initialize the example tab."""
        super().__init__()
        super().setupUi(self)
        self.logger = logger
        self.logger.info("Init third party tab: %s", self.name)
        self.session = session
        self.app_name = app_name
        self.dvn_conf = DVNConf(None)
        self.dvn_api = None
        self.dvn_ops = DvnOperations()
        self.url = None
        self.irods_model = None
        self.init_tab()

    def init_tab(self):
        """Initialise the widgets in the tab."""
        # add Dataverse URLs from config
        self.load_dataverse_conf()
        self.dv_url_select_box.currentTextChanged.connect(self._connect_to_dataverse)

        self.add_url_button.clicked.connect(self.add_dv_url)
        self.delete_url_button.clicked.connect(self.delete_dv_url)
        # self.dv_ds_edit --> get dataset id
        self.dv_ds_edit.textChanged.connect(self.populate_selected_data_table)
        self.dv_create_ds_button.clicked.connect(self.dv_create_ds)
        # self.selected_data_table --> populate
        self.delete_selected_button.clicked.connect(self.dv_rm_file)
        self.dv_push_button.clicked.connect(self.dv_push)
        self.add_selected_button.clicked.connect(self.dv_add_file)
        self.add_selected_button.setEnabled(False)
        # self.irods_tree_view --> load collections
        self._init_irods_tree()

    def load_dataverse_conf(self):
        """Load or refresh drop down menu for configs."""
        items = [
            key for key in self.dvn_conf.dvns.keys() if self.dvn_conf.dvns[key].get("token", None)
        ]
        self.dv_url_select_box.clear()
        self.dv_url_select_box.addItems(items)
        if self.dvn_conf.cur_dvn is not None and self.dvn_conf.cur_dvn in items:
            self.dv_url_select_box.setCurrentIndex(items.index(self.dvn_conf.cur_dvn))
        else:
            self.dv_url_select_box.setCurrentIndex(0)
        self._connect_to_dataverse()

    def _connect_to_dataverse(self):
        self.error_label.clear()
        cur_url = self.dv_url_select_box.currentText()
        if cur_url == "":
            self.error_label.setText("Please create a Dataverse configuration.")
            return
        self.dvn_conf.set_dvn(cur_url)
        url, entry = self.dvn_conf.get_entry(cur_url)
        try:
            self.dvn_api = Dataverse(url, entry["token"])
            self.url = url
            self.dv_ds_edit.clear()
        except Exception as err:  # pylint: disable=W0718
            self.error_label.setText(
                    f"Could not connect to {url} with {entry[1]['token']}, {repr(err)}")

    def add_dv_url(self):
        """Add a new Dataverse URL with parameters."""
        self.error_label.clear()
        url_widget = CreateDvnURL(self.dvn_conf)
        url_widget.exec()
        self.load_dataverse_conf()

    def delete_dv_url(self):
        """Remove a URL from the configurations."""
        cur_url = self.dv_url_select_box.currentText()
        self.dvn_conf.delete_alias(cur_url)
        self.load_dataverse_conf()

    def dv_create_ds(self):
        """Create a dataset."""
        self.error_label.clear()
        if not self.dvn_api:
            self.error_label.setText(
                f"No API connection for {self.dv_url_select_box.currentText()}"
            )
            return
        self.error_label.clear()
        url_widget = CreateDataset(self.dvn_api, self.dv_ds_edit)
        url_widget.exec()
        doi = self.dv_ds_edit.text()
        self.logger.info("DATAVERSE: Created Dataset %s", doi)

    def dv_rm_file(self):
        """Remove a file from the table of selected files."""
        self.error_label.clear()
        dataset_id = self.dv_ds_edit.text()
        rows = set(idx.row() for idx in self.selected_data_table.selectedIndexes())
        for row in rows:
            path = self.selected_data_table.item(row, 0).text()
            self.dvn_ops.rm_file(self.url, dataset_id, path)
        self.populate_selected_data_table()

    def dv_push(self):
        """Download all objects in the table and upload to Dataverse dataset."""
        self.error_label.clear()
        dataset_id = self.dv_ds_edit.text()
        if dataset_id == "":
            self.error_label.setText("Select a dataset and refresh table.")
            return
        if not self.dvn_api.dataset_exists(dataset_id):
            self.error_label.setText("Dataset does not exist (any longer).")
            return
        if self.selected_data_table.rowCount() == 0:
            self.error_label.setText("Please add some data from the iRODS tree.")
            return

        temp_dir = Path.home() / ".dvn" / "data"
        temp_dir.mkdir(exist_ok=True)
        self.logger.info("DATAVERSE: Download data from iRODS to  %s", str(temp_dir))

        for row in range(self.selected_data_table.rowCount()):
            irods_path = IrodsPath(self.session, self.selected_data_table.item(row, 0).text())
            if irods_path.dataobject_exists():
                try:
                    local_path = create_unique_filename(temp_dir, irods_path.name)
                    download(self.session, irods_path, local_path, overwrite=True)
                    self.logger.info(
                        "DATAVERSE: Download %s --> %s", str(irods_path), str(local_path)
                    )
                    self.dvn_api.add_datafile_to_dataset(dataset_id, local_path)
                    self.logger.info("DATAVERSE: Upload %s --> %s", str(local_path), dataset_id)
                    self.dvn_ops.rm_file(self.url, dataset_id, str(irods_path))
                    local_path.unlink()
                except Exception as err:  # pylint: disable=W0718
                    self.logger.error("DATAVERSE: Error in download and upload: %s", repr(err))
                    self.error_label.setText("Something went wrong, please check the logs.")
        self.populate_selected_data_table()
        shutil.rmtree(temp_dir)

    def dv_add_file(self):
        """Add file from irods tree to table with selected files."""
        self.error_label.clear()
        # Retrieve irods paths
        irods_selection = self.irods_tree_view.selectedIndexes()
        if len(irods_selection) == 0:
            self.error_label.setText("Please select a data object.")
            return
        for idx in irods_selection:
            irods_path = self.irods_model.irods_path_from_tree_index(idx)
            if irods_path.dataobject_exists():
                self.dvn_ops.add_file(self.url, self.dv_ds_edit.text(), str(irods_path))
            else:
                print("Not a data object")
                self.error_label.setText("Please only select data objects.")
        self.populate_selected_data_table()

    def irods_root(self):
        """Retrieve lowest visible level in the iRODS tree for the user."""
        lowest = IrodsPath(self.session).absolute()
        while lowest.parent.exists() and str(lowest) != "/":
            lowest = lowest.parent
        return lowest

    def _init_irods_tree(self):
        root = self.irods_root()
        self.irods_model = IrodsTreeModel(self.irods_tree_view, root)
        self.irods_tree_view.setModel(self.irods_model)
        # self.irods_tree_view.headerItem().setText(0, "")
        self.irods_tree_view.expanded.connect(self.irods_model.refresh_subtree)
        self.irods_model.init_tree()
        # self.irods_tree_view.setCurrentIndex(self.irods_model.index(0, 0))
        self.irods_tree_view.expand(self.irods_model.index(0, 0))

        # hide unnecessary information
        self.irods_tree_view.setColumnHidden(1, True)
        self.irods_tree_view.setColumnHidden(2, True)
        self.irods_tree_view.setColumnHidden(3, True)
        self.irods_tree_view.setColumnHidden(4, True)
        self.irods_tree_view.setColumnHidden(5, True)

    def populate_selected_data_table(self):
        """Load irods path and size into table."""
        self.add_selected_button.setEnabled(True)
        self.selected_data_table.setRowCount(0)
        dataset_id = self.dv_ds_edit.text()
        # gather data from current stored files
        if dataset_id != "" and self.dvn_api.dataset_exists(dataset_id):
            if self.dvn_ops.get_paths(self.url, dataset_id):
                current_paths = [
                    (IrodsPath(self.session, path), IrodsPath(self.session, path).size)
                    for path in self.dvn_ops.get_paths(self.url, dataset_id)
                ]
                populate_table(self.selected_data_table, len(current_paths), current_paths)
            else:
                self.error_label.setText("No data files stored for dataset.")
        else:
            self.error_label.setText("Enter a valid Dataset Idenitifier.")
