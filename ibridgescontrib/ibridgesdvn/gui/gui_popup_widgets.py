"""Popoup widgets for Dataverse Tab."""

import json
from pathlib import Path

import PySide6.QtCore
from pyDataverse.exceptions import ApiAuthorizationError
from pyDataverse.utils import read_file
from PySide6.QtWidgets import QFileDialog

from ibridgescontrib.ibridgesdvn.ds_meta import (
    DATAVERSE_SUBJECTS,
    build_metadata,
    is_valid_email,
    is_valid_name,
)
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations
from ibridgescontrib.ibridgesdvn.gui.uiCreateDataset import Ui_Dialog as ui_create_dataset
from ibridgescontrib.ibridgesdvn.gui.uiCreateMetadata import Ui_Dialog as ui_create_metadata
from ibridgescontrib.ibridgesdvn.gui.uiCreateUrl import Ui_Dialog as ui_create_url


class CreateDataset(PySide6.QtWidgets.QDialog, ui_create_dataset):
    """Popup window to create a new dataset."""

    def __init__(self, dvn_api, return_label):
        super().__init__()
        super().setupUi(self)

        self.dvn_api = dvn_api
        self.return_label = return_label

        self.setWindowTitle("Create new Dataset.")
        self.setWindowFlags(PySide6.QtCore.Qt.WindowType.WindowStaysOnTopHint)

        # Connect signals
        self.ok_button.clicked.connect(self.create)
        self.cancel_button.clicked.connect(self.close)
        self.load_json_button.clicked.connect(self.select_meta_file)
        self.create_json_button.clicked.connect(self.create_meta)

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def close(self):
        self.done(0)

    def _set_error(self, msg):
        self.error_label.setText(msg)

    def _get_metadata_json(self):
        """Return metadata JSON string or None."""
        if self.json_file_label.text():
            try:
                return read_file(self.json_file_label.text())
            except Exception as err:
                self._set_error(f"Could not read JSON file: {err}")
                return None

        text = self.meta_browser.toPlainText().strip()
        return text if text else None

    # ------------------------------------------------------------------
    # Main create logic
    # ------------------------------------------------------------------

    def create(self):
        dv = self.dv_edit.text().strip()
        if not dv:
            self._set_error("Please provide a Dataverse collection.")
            return

        metadata_json = self._get_metadata_json()
        if not metadata_json:
            self._set_error("Please choose a metadata JSON file or create metadata.")
            return

        # Validate dataverse exists
        try:
            if not self.dvn_api.dataverse_exists(dv):
                self._set_error(f"Could not find {dv}.")
                return
        except ApiAuthorizationError:
            self._set_error(
                f"Authorization Error: token invalid for {self.dvn_api.url}."
            )
            return

        # Create dataset
        try:
            response = self.dvn_api.create_dataset_from_json(dv, metadata_json)
            data = response.get("data", {})
            pid = data.get("persistentId")

            if not pid:
                self._set_error(f"ERROR: Could not create Dataset. {response}")
                return

            doi = pid.split(":")[1]
            ops = DvnOperations()
            ops.register_created_dataset(self.dvn_api.url, pid)
            self.return_label.setText(doi)
            self.done(0)

        except ApiAuthorizationError as err:
            self._set_error(f"ERROR: Could not create Dataset. {repr(err)}")

    # ------------------------------------------------------------------
    # Metadata file selection
    # ------------------------------------------------------------------

    def select_meta_file(self):
        select_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select JSON file",
            str(Path("~").expanduser()),
            "JSON Files (*.json);;All Files (*)",
        )

        if select_file:
            self.json_file_label.setText(select_file)
            try:
                self.meta_browser.setText(read_file(select_file))
            except Exception as err:
                self._set_error(f"Could not read file: {err}")

    # ------------------------------------------------------------------
    # Metadata creation popup
    # ------------------------------------------------------------------

    def create_meta(self):
        self.json_file_label.clear()
        self.meta_browser.clear()
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
            self.error_label.setText("No metadata provided.")
            return

        try:
            json_string = json.dumps(build_metadata(json.loads(text)), indent=2)
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
        self.error_label.setWordWrap(True)

    def close(self):
        """Close widget."""
        self.done(0)

    def create(self):
        """Create new Dataverse configuration."""
        self.error_label.clear()
        url = self.url_edit.text().strip()
        token = self.token_edit.text().strip()
        alias = self.alias_edit.text().strip()
    
        # Validate input
        error = self._input_is_invalid(url, token)
        if error:
            self.error_label.setText(error)
            return
    
        # 1. Ensure URL entry exists (create if missing)
        try:
            # URL already exists → get it
            existing_url, entry = self.dvn_conf.get_entry(url)
        except KeyError:
            # URL does not exist → create new entry
            try:
                self.dvn_conf.add_dataverse(url, alias=None)
            except ValueError as exc:
                self.error_label.setText(str(exc))
                return
            existing_url, entry = self.dvn_conf.get_entry(url)
    
        # 2. If alias provided → assign/update alias
        if alias:
            try:
                self.dvn_conf.update_alias(existing_url, alias)
            except ValueError as exc:
                self.error_label.setText(str(exc))
                return
    
        # 3. Store token
        self.dvn_conf.set_token(existing_url, token)
    
        # Close dialog
        self.done(0)


    def _input_is_invalid(self, url, token):
        if url == "" or not self.dvn_conf.is_valid_url(url):
            return "Please provide a valid URL."
        if token == "":
            return "Please provide a token."

        return None
