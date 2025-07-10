"""Example tab class to extend the iBridgesGUI app."""
import logging

import PySide6.QtWidgets
from ibridges.session import Session

from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf
from ibridgescontrib.ibridgesdvn.gui_popup_widgets import CreateDvnURL
from ibridgescontrib.ibridgesdvn.uiDataverse import Ui_tabDataverse


class DataverseTab(PySide6.QtWidgets.QWidget, Ui_tabDataverse):
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
        self.init_tab()

    def init_tab(self):
        """Initialise the widgets in the tab."""
        # add Dataverse URLs from config
        self.load_dataverse_conf()
        self.dv_url_select_box.currentTextChanged.connect(self.dvn_conf.set_dvn)

        self.add_url_button.clicked.connect(self.add_dv_url)
        self.add_url_button.setToolTip("Create a new Dataverse configuration.")
        self.delete_url_button.clicked.connect(self.delete_dv_url)
        self.delete_url_button.setToolTip("Delete a Dataverse configuration.")
        #self.dv_ds_edit --> get dataset id
        self.dv_create_ds_button.clicked.connect(self.dv_create_ds)
        self.dv_create_ds_button.setToolTip("Create new dataset.")
        #self.selected_data_table --> populate
        self.delete_selected_button.clicked.connect(self.dv_rm_file)
        self.delete_selected_button.setToolTip("Remove file from table.")
        self.dv_push_button.clicked.connect(self.dv_push)
        self.dv_push_button.setToolTip("Upload to Dataverse dataset.")
        self.add_selected_button.clicked.connect(self.dv_add_file)
        self.add_selected_button.setToolTip("Mark file(s) for upload to Dataverse.")
        #self.irods_tree_view --> load collections

    def load_dataverse_conf(self):
        """Load or refresh drop down menu for configs."""
        items = [key for key in self.dvn_conf.dvns.keys()
                        if self.dvn_conf.dvns[key].get("token", None)]
        self.dv_url_select_box.clear()
        self.dv_url_select_box.addItems(items)
        if self.dvn_conf.cur_dvn is not None and self.dvn_conf.cur_dvn in items:
            self.dv_url_select_box.setCurrentIndex(items.index(self.dvn_conf.cur_dvn))
        else:
            self.dv_url_select_box.setCurrentIndex(0)


    def add_dv_url(self):
        """Add a new Dataverse URL with parameters."""
        self.error_label.clear()
        url_widget = CreateDvnURL(self.dvn_conf)
        url_widget.exec()
        self.load_dataverse_conf()

    def delete_dv_url(self):
        """Remove a URL from the configurations."""
        cur_url = self.dv_url_select_box.currentText()
        print("delete", cur_url)
        self.dvn_conf.delete_alias(cur_url)
        self.load_dataverse_conf()

    def dv_create_ds(self):
        """Create a dataset."""
        print("not implemented")

    def dv_rm_file(self):
        """Remove a file from the table of selected files."""
        print("not implemented")

    def dv_push(self):
        """Download all objects in the table and upload to Dataverse dataset."""
        print("not implemented")

    def dv_add_file(self):
        """Add file from irods tree to table with selected files."""
        print("not implemented")


    #    """Retrieve info from session and print it to tab elements."""
    #    self.server.setText(self.session.irods_session.host)
    #    self.port.setText(str(self.session.irods_session.port))
    #    self.home.setText(self.session.home)
    #    self.user.setText(self.session.irods_session.username)
