"""Popoup widgets for Dataverse Tab."""

from pathlib import Path

import PySide6.QtCore
from PySide6.QtWidgets import QFileDialog

from ibridgescontrib.ibridgesdvn.uiCreateDataset import Ui_Dialog as ui_create_dataset
from ibridgescontrib.ibridgesdvn.uiCreateUrl import Ui_Dialog as ui_create_url
from ibridgescontrib.ibridgesdvn.uiCreateMetadata import Ui_Dialog as ui_create_metadata
from ibridgescontrib.ibridgesdvn.ds_meta import DATAVERSE_SUBJECTS

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
        self.create_json_button.clicked.connect(self.create_meta)
        self.return_label = return_label

    def close(self):
        """Close widget."""
        self.done(0)

    def create(self):
        """Create new Dataverse configuration."""
        dv = self.dv_edit.text()
        if dv == "":
            self.error_label.setText("Please provide a Dataverse collection.")
            return
        if self.json_file_label.text() == "":
            self.error_label.setText("Please choose a metadata json file or create metadata.")
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

    def create_meta(self):
        """Open pop up to fetch minimal metadata."""
        meta_widget = CreateMetadata(self.meta_browser)
        meta_widget.exec()


class CreateMetadata(PySide6.QtWidgets.QDialog, ui_create_metadata):
    """Popup window to fetch dataset metadata."""

    def __init__(self, metadata_field):
        """Init window."""
        super().__init__()
        super().setupUi(self)
        self.setWindowTitle("Create Metadata for Dataset.")
        self.setWindowFlags(PySide6.QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.metadata_field = metadata_field

        self.ok_button.clicked.connect(self.submit)
        self.cancel_button.clicked.connect(self.close)

        #populate subjects
        self.subject_box.addItems([s for s in DATAVERSE_SUBJECTS])

        self.author_button.clicked.connect(self.parse_author)
        self.contact_button.clicked.connect(self.parse_contact)
        self.subject_button.clicked.connect(self.parse_subject)

    def close(self):
        """Close widget."""
        self.done(0)

    def submit(self):
        """Submit info to parent."""
        text = self.json_edit.toPlainText()
        self.metadata_field.setText(text)

    def parse_subject(self):
        """Parse, title, subject and description."""
        title = self.title_edit.text()
        subject = self.subject_box.currentText()
        description = self.description_edit.text()
        print(title, subject, description)
        self.title_edit.clear()
        self.description_edit.clear()
    
    def parse_contact(self):
        """Parse contact."""
        contactname = self.contact_name_edit.text()
        conatctmail = self.contact_email_edit.text()
        print(contactname, conatctmail)
        self.contact_name_edit.clear()
        self.contact_mail_edit.clear()

    def parse_author(self):
        """Parse author."""
        authorname = self.author_edit.text()
        authoraff = self.affiliation_edit.text()
        print(authorname, authoraff)
        self.author_edit.clear()
        self.affiliation_edit.clear()

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
