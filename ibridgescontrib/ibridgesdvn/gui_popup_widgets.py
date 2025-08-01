"""Popoup widgets for Dataverse Tab."""

import json
from pathlib import Path

import PySide6.QtCore
from pyDataverse.utils import read_file
from PySide6.QtWidgets import QFileDialog

from ibridgescontrib.ibridgesdvn.ds_meta import (
    DATAVERSE_SUBJECTS,
    build_metadata,
    is_valid_email,
    is_valid_name,
)
from ibridgescontrib.ibridgesdvn.uiCreateDataset import Ui_Dialog as ui_create_dataset
from ibridgescontrib.ibridgesdvn.uiCreateMetadata import Ui_Dialog as ui_create_metadata
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
        if self.json_file_label.text() == "" and self.meta_browser.toPlainText() == "":
            self.error_label.setText("Please choose a metadata json file or create metadata.")
            return

        if not self.dvn_api.dataverse_exists(dv):
            self.error_label.setText(f"Could not find {dv}.")
            return

        if self.json_file_label.text() != "":
            meta_json = self.json_file_label.text()
            response = self.dvn_api.create_dataset_with_json(dv, meta_json)
            doi = response.json()["data"]["persistentId"].split(":")[1]
            self.return_label.setText(doi)
            self.done(0)
        elif self.meta_browser.toPlainText() != "":
            response = self.dvn_api.create_dataset(dv, self.meta_browser.toPlainText())
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
        self.meta_browser.setText(read_file(str(select_file)))

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

        # populate subjects
        self.subject_box.addItems(DATAVERSE_SUBJECTS)

        self.author_button.clicked.connect(self.parse_author)
        self.contact_button.clicked.connect(self.parse_contact)
        self.subject_button.clicked.connect(self.parse_subject)

        # gather input for compound entries
        self.show_items_as_text = {}
        self.descriptions = []
        self.subjects = []
        self.contacts = []
        self.authors = []
        self.title = ""

    def close(self):
        """Close widget."""
        self.done(0)

    def submit(self):
        """Submit info to parent."""
        text = self.json_edit.toPlainText()

        if text == "":
            self.error_label("No metadata provided.")
            return

        try:
            json_string = build_metadata(json.loads(text))
            self.metadata_field.setText(json_string)
            self.close()
        except json.JSONDecodeError as e:
            self.error_label.setText(f"Cannot convert to json, {repr(e)}")
        except KeyError as e:
            self.error_label.setText(f"Cannot create json, key missing, {repr(e)}")

    def _get_current_json(self):
        self.error_label.clear()
        text = self.json_edit.toPlainText()
        if text == "":
            self.error_label.setText("No metadata set.")
        else:
            try:
                json_data = json.loads(text)
                self.descriptions = json_data.get("descriptions", [])
                self.subjects = json_data.get("subjects", [])
                self.authors = json_data.get("authors", [])
                self.contacts = json_data.get("contacts", [])
                self.title = json_data.get("title", "")
            except json.JSONDecodeError as e:
                self.error_label.setText(f"Invalid JSON: {e}")

    def parse_subject(self):
        """Parse, title, subject and description."""
        self._get_current_json()
        self.error_label.clear()
        self.title = self.title_edit.text().strip() if self.title_edit.text() != "" else self.title
        subject = self.subject_box.currentText().strip()
        desc = self.description_edit.text().strip()
        if desc:
            self.descriptions.append(
                {
                    "dsDescriptionValue": {
                        "value": desc,
                        "multiple": False,
                        "typeClass": "primitive",
                        "typeName": "dsDescriptionValue",
                    }
                }
            )
        if subject not in self.subjects:
            self.subjects.append(subject)
        self.show_items_as_text["subjects"] = self.subjects
        if self.title != "":
            self.show_items_as_text["title"] = self.title
        if self.descriptions:
            self.show_items_as_text["descriptions"] = self.descriptions

        self.json_edit.setText(json.dumps(self.show_items_as_text, indent=2))

        self.title_edit.clear()
        self.description_edit.clear()

    def parse_contact(self):
        """Parse contact."""
        self._get_current_json()
        self.error_label.clear()

        contactname = self.contact_name_edit.text().strip()
        if contactname and not is_valid_name(contactname):
            self.error_label.setText("Contact: Invalid format for name. Use 'Last, First'.")
            return

        contactemail = self.contact_email_edit.text().strip()
        if contactemail and not is_valid_email(contactemail):
            self.error_label.setText("Contact: Invalid format for mail.")
            return

        if contactname and contactemail:
            self.contacts.append(
                {
                    "datasetContactName": {
                        "value": contactname,
                        "typeClass": "primitive",
                        "multiple": False,
                        "typeName": "datasetContactName",
                    },
                    "datasetContactEmail": {
                        "value": contactemail,
                        "typeClass": "primitive",
                        "multiple": False,
                        "typeName": "datasetContactEmail",
                    },
                }
            )
            self.show_items_as_text["contacts"] = self.contacts
            self.json_edit.setText(json.dumps(self.show_items_as_text, indent=2))

            self.contact_name_edit.clear()
            self.contact_email_edit.clear()

    def parse_author(self):
        """Parse author."""
        self._get_current_json()
        self.error_label.clear()

        authorname = self.author_edit.text().strip()
        authoraff = self.affiliation_edit.text().strip()
        if authorname and not is_valid_name(authorname):
            self.error_label.setText("Author: Invalid format for name. Use 'Last, First'.")
        if authorname and authoraff:
            self.authors.append(
                {
                    "authorName": {
                        "value": authorname,
                        "typeClass": "primitive",
                        "multiple": False,
                        "typeName": "authorName",
                    },
                    "authorAffiliation": {
                        "value": authoraff,
                        "typeClass": "primitive",
                        "multiple": False,
                        "typeName": "authorAffiliation",
                    },
                }
            )
            self.show_items_as_text["authors"] = self.authors
            self.json_edit.setText(json.dumps(self.show_items_as_text, indent=2))

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
