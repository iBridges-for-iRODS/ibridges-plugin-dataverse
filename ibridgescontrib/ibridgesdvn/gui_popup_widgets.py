"""Popoup widgets for Dataverse Tab."""

from pathlib import Path

import PySide6.QtCore
from PySide6.QtWidgets import QFileDialog

from ibridgescontrib.ibridgesdvn.uiCreateDataset import Ui_Dialog as ui_create_dataset
from ibridgescontrib.ibridgesdvn.uiCreateUrl import Ui_Dialog as ui_create_url


class CreateDataset(PySide6.QtWidgets.QDialog, ui_create_dataset):
    """Popup window to create a new dataset."""

    def __init__(self, dvn_api, return_label):
        """Init window."""
        super().__init__()
        super().setupUi(self)
        self.dvn_api = dvn_api
        self.setWindowTitle("Create new Dataset.")
        self.setWindowFlags(PySide6.QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.ok_button.clicked.connect(self.create)
        self.cancel_button.clicked.connect(self.close)
        self.load_json_button.clicked.connect(self.select_meta_file)
        self.return_label = return_label

    def close(self):
        """Close widget."""
        self.done(0)

    def create(self):
        """Create new Dataverse configuration."""
        dv = self.dv_edit.text()
        if dv == "":
            self.error_label.text("Please provide a Dataverse collection.")
            return
        if self.json_file_label.text() == "":
            self.error_label.setText("Please choose a metadata json file.")
            return
        if not self.dvn_api.dataverse_exists(dv):
            self.error_label.setText(f"Could not find {dv}.")
            return

        meta_json = self.json_file_label.text()
        response = self.dvn_api.create_dataset_with_json(dv, meta_json)
        doi = response.json()["data"]["persistentId"].split(":")[1]
        self.return_label.setText(doi)
        self.done(0)

    def select_meta_file(self):
        """Open file selector."""
        select_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select JSON file",
            str(Path("~").expanduser()),  # directory (3rd positional argument)
            "JSON Files (*.json);;All Files (*)",  # file filter (4th positional argument)
        )

        self.json_file_label.setText(str(select_file))


class CreateDvnURL(PySide6.QtWidgets.QDialog, ui_create_url):
    """Popup window to create a new URL entry."""

    def __init__(self, dvn_conf):
        """Initialise window."""
        super().__init__()
        super().setupUi(self)
        self.setWindowTitle("Create new Dataverse configuration.")
        self.setWindowFlags(PySide6.QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.ok_button.clicked.connect(self.create)
        self.cancel_button.clicked.connect(self.close)
        self.dvn_conf = dvn_conf

    def close(self):
        """Close widget."""
        self.done(0)

    def create(self):
        """Create new Dataverse configuration."""
        url = self.url_edit.text()
        token = self.token_edit.text()
        alias = self.alias_edit.text()

        check = self._input_is_invalid(url, token)
        if check is False:
            self.dvn_conf.set_dvn(url)
            try:
                _, entry = self.dvn_conf.get_entry()
                entry["token"] = token
            except:  # pylint: disable=W0702 # noqa: E722
                entry = {}
                entry["token"] = token

            if alias:
                entry["alias"] = alias
            self.dvn_conf.dvns[url] = entry
            self.dvn_conf.save()
            self.done(0)
        else:
            self.error_label.setText(check)

    def _input_is_invalid(self, url, token):
        if url == "" or not self.dvn_conf.is_valid_url(url):
            return "Please provide a valid URL."
        if token == "":
            return "Please provide a token."
        return False
