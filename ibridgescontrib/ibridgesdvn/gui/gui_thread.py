"""QThread to transfer data between iRODS and Dataverse."""

from pathlib import Path

import PySide6.QtCore
from ibridges import IrodsPath, Session, download

from ibridgescontrib.ibridgesdvn.dataverse import Dataverse
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations
from ibridgescontrib.ibridgesdvn.utils import (
    calculate_checksum,
    create_unique_filename,
)


class TransferDataThread(PySide6.QtCore.QThread):
    """Background thread to transfer data from iRODS to Dataverse."""

    result = PySide6.QtCore.Signal(dict)
    current_progress = PySide6.QtCore.Signal(list)

    # pylint: disable=too-many-positional-arguments
    def __init__(
        self,
        ienv_path: Path,
        logger,
        dvn_ops: DvnOperations,
        dvn_url: str,
        dvn_token: str,
        tempdir: Path,
        dataset_id: str,
        checksum: bool,
    ):
        """Init transfer."""
        super().__init__()

        self.logger = logger
        self.checksum = checksum
        self.tempdir = tempdir
        self.dataset_id = dataset_id
        self.dvn_url = dvn_url
        self.dvn_ops = dvn_ops

        # Create a dedicated iRODS session for this thread
        self.thread_session = Session(irods_env=ienv_path)
        self.logger.debug("DATAVERSE: Transfer thread: Created new iRODS session.")

        # Resolve iRODS paths from operations log
        self.irods_paths = [
            IrodsPath(self.thread_session, ip)
            for ip in self.dvn_ops.get_paths(self.dvn_url, self.dataset_id)
        ]

        # Dataverse client for upload/checksum
        self.dvn_api = Dataverse(self.dvn_url, dvn_token)

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _download_file(self, irods_path: IrodsPath) -> Path:
        """Download a file from iRODS to a unique temporary location."""
        local_path = create_unique_filename(self.tempdir, irods_path.name)
        download(irods_path, local_path, overwrite=True)
        self.logger.info("DATAVERSE: Download %s --> %s", irods_path, local_path)
        return local_path

    def _upload_file(self, local_path: Path):
        """Upload a local file to Dataverse."""
        self.dvn_api.add_datafile_to_dataset(self.dataset_id, local_path)
        self.logger.info("DATAVERSE: Upload %s --> %s", local_path, self.dataset_id)

    def _verify_checksum(self, local_path: Path, irods_path: IrodsPath) -> bool:
        """Verify checksum after upload."""
        alg, dvn_checksum = self.dvn_api.get_checksum_by_filename(self.dataset_id, local_path.name)
        local_checksum = calculate_checksum(local_path, alg=alg)

        if local_checksum != dvn_checksum:
            self.logger.error(
                "DATAVERSE: Checksum mismatch for %s --> %s",
                local_path,
                self.dataset_id,
            )
            return False

        self.logger.info("DATAVERSE: Checksum OK for %s --> %s", irods_path, self.dataset_id)
        return True

    def _cleanup_file(self, irods_path: IrodsPath, local_path: Path):
        """Remove file from pending list and delete local temp file."""
        self.dvn_ops.rm_file(self.dvn_url, self.dataset_id, str(irods_path))
        local_path.unlink(missing_ok=True)

    def _delete_session(self):
        """Clean up iRODS and Dataverse sessions."""
        self.thread_session.close()
        del self.dvn_api

        if self.thread_session.irods_session is None:
            self.logger.debug("DATAVERSE: Transfer thread session deleted.")
        else:
            self.logger.debug("DATAVERSE: Transfer thread session still active.")

    # ------------------------------------------------------------------
    # Main thread execution
    # ------------------------------------------------------------------

    def run(self):
        """Execute the transfer process."""
        file_ok = 0
        file_failed = 0
        transfer_out = {"error": ""}

        total_files = len(self.irods_paths)

        for irods_path in self.irods_paths:
            if not irods_path.dataobject_exists():
                msg = f"{irods_path} not found in iRODS."
                self.logger.error("DATAVERSE: %s", msg)
                transfer_out["error"] += f"\n{msg}"
                file_failed += 1
                self.current_progress.emit([file_ok, total_files, file_failed])
                continue

            try:
                # Download
                local_path = self._download_file(irods_path)

                # Upload
                self._upload_file(local_path)

                # Optional checksum verification
                if self.checksum:
                    if not self._verify_checksum(local_path, irods_path):
                        transfer_out["error"] += f"\nChecksum error for {irods_path}."
                        file_failed += 1
                    else:
                        file_ok += 1
                else:
                    file_ok += 1

                # Cleanup
                self._cleanup_file(irods_path, local_path)

            except Exception as err:  # pylint: disable=broad-except
                self.logger.error("DATAVERSE: Transfer error: %s", repr(err))
                transfer_out["error"] += "\nSomething went wrong, check logs."
                file_failed += 1

            # Emit progress update
            self.current_progress.emit([file_ok, total_files, file_failed])

        # Final cleanup
        self._delete_session()
        self.result.emit(transfer_out)
