"""Manage drafts and the ops log."""
class DraftManager:
    """Handles loading, selecting, and syncing Dataverse drafts."""

    def __init__(self, draft_box, dvn_ops, error_label):
        """Init."""
        self.draft_box = draft_box
        self.dvn_ops = dvn_ops
        self.error_label = error_label

        self.dvn_api = None
        self.url = None

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------

    def update_connection(self, dvn_api, url):
        """Update API + URL when Dataverse changes."""
        self.dvn_api = dvn_api
        self.url = url

    def load_drafts(self):
        """Load drafts into the combobox."""
        self.draft_box.clear()

        if not self.dvn_api or not self.url:
            return

        drafts = self.dvn_ops.get_created_datasets(self.url)

        for ds in drafts:
            try:
                state = self.dvn_api.get_dataset_state(ds)
            except Exception:
                state = "UNKNOWN"

            display = f"{ds} [{state}]"
            self.draft_box.addItem(display, userData=ds)

    def select_first(self):
        """Select the first draft if available."""
        if self.draft_box.count() > 0:
            self.draft_box.setCurrentIndex(0)
            return True
        return False

    def get_selected_dataset_id(self):
        """Return the dataset ID of the selected draft."""
        idx = self.draft_box.currentIndex()
        if idx < 0:
            return None
        return self.draft_box.itemData(idx)

    def sync_dataset(self, dataset_id):
        """Ensure the combobox reflects the given dataset ID."""
        # Check if dataset already exists
        for i in range(self.draft_box.count()):
            if self.draft_box.itemData(i) == dataset_id:
                self.draft_box.setCurrentIndex(i)
                return

        # Otherwise add it
        try:
            state = self.dvn_api.get_dataset_state(dataset_id)
            self.dvn_ops.register_created_dataset(self.url, dataset_id)
        except Exception:
            state = "UNKNOWN"

        display = f"{dataset_id} [{state}]"
        self.draft_box.addItem(display, userData=dataset_id)
        self.draft_box.setCurrentIndex(self.draft_box.count() - 1)
