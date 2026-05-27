"""Thread to pull data from irods and push to dataverse."""
import shutil


class PushWorkflowManager:
    """Handles the Dataverse push/upload workflow."""

    def __init__(
        self,
        dvn_api_getter,
        url_getter,
        dvn_conf,
        dvn_ops,
        temp_dir,
        get_dataset_id,
        get_row_count,
        create_transfer_thread,
        update_table,
        set_status,
        set_error,
        set_progress,
        enable_gui,
        clear_selection,
        get_checksum_flag,
    ):
        """Init."""
        self.dvn_api_getter = dvn_api_getter
        self.url_getter = url_getter
        self.dvn_conf = dvn_conf
        self.dvn_ops = dvn_ops
        self.temp_dir = temp_dir

        self.get_dataset_id = get_dataset_id
        self.get_row_count = get_row_count
        self.create_transfer_thread = create_transfer_thread

        self.update_table = update_table
        self.set_status = set_status
        self.set_error = set_error
        self.set_progress = set_progress
        self.enable_gui = enable_gui
        self.clear_selection = clear_selection
        self.get_checksum_flag = get_checksum_flag

        self.transfer_thread = None

    def push(self):
        """Entry point for pushing files to Dataverse."""
        dvn_api = self.dvn_api_getter()
        url = self.url_getter()
        dataset_id = self.get_dataset_id()

        if not dvn_api:
            self.set_error("Not connected to Dataverse.")
            return

        if not dataset_id or not dvn_api.dataset_exists(dataset_id):
            self.set_error("Enter a valid Dataset Identifier.")
            return

        state = dvn_api.get_dataset_state(dataset_id)
        if state.lower() != "draft":
            self.set_error(f"Dataset {dataset_id} not in DRAFT state --> {state}")
            return

        row_count = self.get_row_count()
        if row_count == 0:
            self.set_error("Please add some data from the iRODS tree.")
            return

        # Prepare temp dir
        self.temp_dir.mkdir(exist_ok=True)
        token = self.dvn_conf.get_token(url)

        try:
            self.transfer_thread = self.create_transfer_thread(
                url=url,
                token=token,
                dataset_id=dataset_id,
                checksum=self.get_checksum_flag(),
            )
        except Exception as err:
            self.set_error(f"Could not instantiate a new session: {repr(err)}")
            return

        # Connect signals
        self.transfer_thread.current_progress.connect(self._on_progress)
        self.transfer_thread.result.connect(self._on_finished)
        self.transfer_thread.finished.connect(self._on_cleanup)

        # Disable GUI
        self.enable_gui(False)
        self.set_progress(0, row_count)

        self.transfer_thread.start()

    def _on_progress(self, state):
        obj_count, num_objs, obj_failed = state
        self.set_progress(obj_count, num_objs)
        self.set_status(f"{obj_count} of {num_objs} files; failed: {obj_failed}.")

    def _on_finished(self, result):
        if result["error"]:
            self.set_error(result["error"])
            self.update_table()
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            return

        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.update_table()
        self.set_status("")
        self.set_error("Transfer finished, visit Dataverse to publish.")
        self.enable_gui(True)

    def _on_cleanup(self):
        self.enable_gui(True)
        if self.transfer_thread:
            del self.transfer_thread
