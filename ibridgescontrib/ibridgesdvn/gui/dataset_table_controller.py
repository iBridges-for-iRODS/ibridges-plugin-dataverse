"""Table logic."""

from PySide6.QtWidgets import QTableWidgetItem


class DatasetTableController:
    """Encapsulates logic for dataset ID changes and table population."""

    def __init__(
        self,
        table_widget,
        ds_edit,
        error_label,
        dvn_api,
        dvn_ops,
        url,
        irods_session,
        sync_draft_box_callback,
    ):
        """Init."""
        self.table = table_widget
        self.ds_edit = ds_edit
        self.error_label = error_label
        self.dvn_api = dvn_api
        self.dvn_ops = dvn_ops
        self.url = url
        self.irods_session = irods_session
        self.sync_draft_box = sync_draft_box_callback

    def dataset_edit_action(self):
        """Triggered when the dataset ID text changes."""
        self.error_label.clear()
        self.populate_table()

    def populate_table(self):
        """Populate the table with staged files for the dataset."""
        self.table.setRowCount(0)

        dataset_id = self.ds_edit.text().strip()

        # --- Validation ---
        if not self.dvn_api:
            self.error_label.setText(
                "Not connected to Dataverse. Check Dataverse URL and Configuration."
            )
            return

        if not dataset_id:
            self.error_label.setText("Enter a valid Dataset Identifier.")
            return

        if not self.dvn_api.dataset_exists(dataset_id):
            self.error_label.setText("Dataset does not exist (any longer).")
            return

        # Sync draft box
        self.sync_draft_box(dataset_id)

        # --- Load staged paths ---
        paths = self.dvn_ops.get_paths(self.url, dataset_id)
        if not paths:
            return

        # Convert to IrodsPath objects
        try:
            current_paths = [
                (self._make_irods_path(p), self._make_irods_path(p).size) for p in paths
            ]
        except FileNotFoundError as err:
            self.error_label.setText(f"Cannot load staged file: {err}")
            return

        # --- Fill table ---
        self.table.clearContents()
        self.table.setRowCount(len(current_paths))

        for row, (irods_path, size) in enumerate(current_paths):
            self._set_row(row, irods_path, size)

    def _make_irods_path(self, path):
        from ibridges import IrodsPath

        return IrodsPath(self.irods_session, path)

    def _set_row(self, row, irods_path, size):
        """Fill one row of the table."""
        item_path = QTableWidgetItem(str(irods_path))
        item_path.setToolTip(str(irods_path))
        self.table.setItem(row, 0, item_path)

        item_size = QTableWidgetItem(str(size))
        self.table.setItem(row, 1, item_size)
