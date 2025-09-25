"""QThread to transfer data."""

from pathlib import Path

import PySide6.QtCore
from ibridges import IrodsPath, Session, download

from ibridgescontrib.ibridgesdvn.dataverse import Dataverse
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations
from ibridgescontrib.ibridgesdvn.utils import calculate_sha1_checksum, create_unique_filename


class TransferDataThread(PySide6.QtCore.QThread):
    """Transfer data between local and iRODS."""

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
        """Pass parameters.

        ienv_path : Path
            path to the irods_environment.json to create a new session.
        logger : logging.Logger
            Logger
        irods_paths : list
            List of absolute iRODS paths to be transferred.
        """
        super().__init__()

        self.logger = logger
        self.thread_session = Session(irods_env=ienv_path)
        self.logger.debug("DATAVERSE: Transfer data thread: Created new session.")
        self.dvn_ops = dvn_ops
        self.checksum = checksum
        self.tempdir = tempdir
        self.dataset_id = dataset_id
        self.dvn_url = dvn_url
        self.irods_paths = [
            IrodsPath(self.thread_session, ip)
            for ip in self.dvn_ops.get_paths(self.dvn_url, self.dataset_id)
        ]
        self.dvn_api = Dataverse(self.dvn_url, dvn_token)

    def _delete_session(self):
        self.thread_session.close()
        del self.dvn_api
        if self.thread_session.irods_session is None:
            self.logger.debug(
                "DATAVERSE: Transfer data thread: Thread session successfully deleted."
            )
        else:
            self.logger.debug("DATAVERSE: Transfer data thread: Thread session still exists.")

    def run(self):
        """Run the thread."""
        file_count = 0
        file_failed = 0
        transfer_out = {}
        transfer_out["error"] = ""

        for irods_path in self.irods_paths:
            if irods_path.dataobject_exists():
                try:
                    local_path = create_unique_filename(self.tempdir, irods_path.name)
                    download(self.thread_session, irods_path, local_path, overwrite=True)
                    self.logger.info(
                        "DATAVERSE: Download %s --> %s", str(irods_path), str(local_path)
                    )
                    self.dvn_api.add_datafile_to_dataset(self.dataset_id, local_path)
                    self.logger.info(
                        "DATAVERSE: Upload %s --> %s", str(local_path), self.dataset_id
                    )
                    # check checksums
                    if self.checksum:
                        sha1 = calculate_sha1_checksum(local_path)
                        dvn_sha1 = self.dvn_api.get_checksum_by_filename(
                            self.dataset_id, local_path.name
                        )
                        if sha1 != dvn_sha1:
                            self.logger.error(
                                "DATAVERSE: ERROR: transfer  %s --> %s failed, checksum error",
                                str(local_path),
                                self.dataset_id,
                            )
                            file_failed += 1
                            transfer_out["error"] = (
                                transfer_out["error"]
                                + f"\nTransfer failed, checksum error for {str(irods_path)}."
                            )
                        else:
                            self.logger.info(
                                "DATAVERSE: transfer  %s --> %s checksum ok",
                                str(local_path),
                                self.dataset_id,
                            )
                            file_count += 1
                    self.dvn_ops.rm_file(self.dvn_url, self.dataset_id, str(irods_path))
                    local_path.unlink()

                except Exception as err:  # pylint: disable=W0718
                    self.logger.error("DATAVERSE: Error in download and upload: %s", repr(err))
                    transfer_out["error"] = (
                        transfer_out["error"] + "\nSomething went wrong, check the logs."
                    )
            else:
                self.logger.error("DATAVERSE: ERROR: iRODS %s not found.", str(irods_path))
                file_failed += 1
                transfer_out["error"] = transfer_out["error"] + f"\n{irods_path} not found."
            self.current_progress.emit([file_count, len(self.irods_paths), file_failed])

        self._delete_session()
        self.result.emit(transfer_out)
