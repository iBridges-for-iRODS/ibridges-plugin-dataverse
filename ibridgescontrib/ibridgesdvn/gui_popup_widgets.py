"""Popoup widgets for Dataverse Tab."""

import PySide6.QtCore

from ibridgescontrib.ibridgesdvn.uiCreateUrl import Ui_Dialog


class CreateDvnURL(PySide6.QtWidgets.QDialog, Ui_Dialog):
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
            except: # pylint: disable=W0702 # noqa: E722
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
