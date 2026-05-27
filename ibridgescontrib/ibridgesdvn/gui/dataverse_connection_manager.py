"""Manage Dataverse connection."""
import httpx

from ibridgescontrib.ibridgesdvn.utils import ensure_connection


class DataverseConnectionManager:
    """Encapsulates Dataverse URL + token validation and connection logic."""

    def __init__(self, dvn_conf, url_select_box, error_label):
        """Init."""
        self.dvn_conf = dvn_conf
        self.url_select_box = url_select_box
        self.error_label = error_label

        self.current_url = None
        self.dvn_api = None

    def load_configurations(self):
        """Load Dataverse configurations into the dropdown."""
        self.url_select_box.clear()
        items = []

        for url, entry in self.dvn_conf.dvns.items():
            alias = entry.get("alias") or "[no alias]"
            token = entry.get("token")

            url_status = self._validate_url(url)
            token_status = self._validate_token(url, token, url_status)

            label = f"{alias}  →  {url}  [{url_status}, {token_status}]"
            items.append((label, url))

        for label, url in items:
            self.url_select_box.addItem(label, userData=url)

        # auto-select current Dataverse
        if self.dvn_conf.cur_dvn:
            for i in range(self.url_select_box.count()):
                if self.url_select_box.itemData(i) == self.dvn_conf.cur_dvn:
                    self.url_select_box.setCurrentIndex(i)
                    break

    def connect_current(self):
        """Connect to the Dataverse selected in the dropdown."""
        self.error_label.clear()
        self.dvn_api = None

        self.current_url = self.url_select_box.currentData()
        if not self.current_url:
            self.error_label.setText("Please create a Dataverse configuration.")
            return None

        state, dvn_api, error = ensure_connection(self.dvn_conf, self.current_url)

        if error:
            self.error_label.setText(f"Invalid Dataverse connection: {error}")
            return None

        self.dvn_api = dvn_api
        self.dvn_conf.set_dvn(self.current_url)
        return dvn_api

    def delete_current(self):
        """Delete the currently selected Dataverse configuration."""
        url = self.url_select_box.currentData()
        if not url:
            self.error_label.setText("No Dataverse selected.")
            return

        try:
            self.dvn_conf.delete_alias(url)
        except KeyError:
            # silently ignore missing entries
            pass

        self.load_configurations()

    def add_url(self):
        """Load widget to add new configuration."""
        from ibridgescontrib.ibridgesdvn.gui.gui_popup_widgets import CreateDvnURL

        widget = CreateDvnURL(self.dvn_conf)
        widget.exec()

    def _validate_url(self, url):
        try:
            resp = httpx.get(f"{url}/api/info/version", timeout=3.0)
            return "dataverse OK" if resp.status_code == 200 else "invalid dataverse"
        except Exception:
            return "unreachable"

    def _validate_token(self, url, token, url_status):
        if not token:
            return "no token"
        if url_status != "dataverse OK":
            return "token invalid"

        try:
            resp = httpx.get(
                f"{url}/api/users/:me",
                headers={"X-Dataverse-key": token},
                timeout=3.0,
            )
            return "token OK" if resp.status_code == 200 else "token invalid"
        except Exception:
            return "token invalid"
