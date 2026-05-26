"""Dataverse backend for dataset creation, metadata retrieval, and file upload."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import httpx
from pyDataverse.api import NativeApi
from pyDataverse.exceptions import ApiAuthorizationError
from pyDataverse.models import Datafile, Dataset


class Dataverse:
    """A backend wrapper around Dataverse operations.

    Responsibilities:
    - Authentication
    - Dataset creation
    - Dataset metadata retrieval
    - File upload
    - File checksum lookup
    - Max upload size lookup
    """

    def __init__(self, url: str, token: str) -> None:
        """Initialize the Dataverse client with base URL and API token."""
        if not token:
            raise ValueError("Dataverse API token cannot be empty.")

        self.url = url.rstrip("/")
        self.token = token

        if not self._token_valid():
            raise ApiAuthorizationError("Dataverse and API token do not match.")

        self.api = NativeApi(self.url, self.token)
        self.http = httpx.Client(
            base_url=self.url,
            headers={"X-Dataverse-key": self.token},
            timeout=30.0,
        )

    def _token_valid(self) -> bool:
        """Return True if the API token is valid for this Dataverse instance."""
        try:
            resp = httpx.get(
                f"{self.url}/api/users/:me",
                headers={"X-Dataverse-key": self.token},
                timeout=5.0,
            )
            return resp.status_code == 200
        except Exception:
            return False

    def dataverse_exists(self, alias: str) -> bool:
        """Return True if a dataverse with the given alias exists."""
        resp = self.api.get_dataverse(alias)
        return resp.status_code == 200

    def get_dataverse_info(self, alias: str) -> Dict[str, Any]:
        """Return metadata for the specified dataverse."""
        return self.api.get_children(alias)

    def list_dataverse_content(self, alias: str) -> Dict[str, Any]:
        """Return the contents of a dataverse using the native Dataverse API."""
        resp = self.http.get(f"/api/dataverses/{alias}/contents")
        resp.raise_for_status()
        return resp.json()

    def _normalize_bare_id(self, dataset_id: str) -> str:
        """Return the dataset ID without a doi: prefix."""
        if dataset_id.startswith("doi:"):
            return dataset_id[4:]
        return dataset_id

    def _to_doi(self, dataset_id: str) -> str:
        """Return the dataset ID with a doi: prefix."""
        bare = self._normalize_bare_id(dataset_id)
        return f"doi:{bare}"

    def dataset_exists(self, dataset_id: str) -> bool:
        """Return True if a dataset with the given ID exists."""
        pid = self._to_doi(dataset_id)
        resp = self.api.get_dataset(pid)
        return resp.status_code in range(200, 300)

    def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """Return full dataset metadata for the given dataset ID."""
        pid = self._to_doi(dataset_id)
        resp = self.api.get_dataset(pid)
        resp.raise_for_status()
        return resp.json()

    def get_dataset_state(self, dataset_id: str) -> str:
        """Return the Dataverse versionState for the dataset."""
        info = self.get_dataset_info(dataset_id)
        return info["data"]["latestVersion"]["versionState"]

    def is_dataset_published(self, dataset_id: str) -> bool:
        """Return True if the dataset is in RELEASED state."""
        state = self.get_dataset_state(dataset_id)
        return state.upper() == "RELEASED"

    def create_dataset_from_json(self, dataverse: str, metadata_json: str) -> Dict[str, Any]:
        """Create a dataset using a JSON metadata string."""
        if not dataverse:
            raise ValueError("Dataverse name must not be empty.")
        if not metadata_json:
            raise ValueError("Metadata JSON must not be empty.")

        ds = Dataset()
        ds.from_json(metadata_json)

        if not ds.validate_json():
            raise ValueError("Invalid dataset metadata JSON.")

        resp = self.api.create_dataset(dataverse, ds.json())
        resp.raise_for_status()
        return resp.json()

    def delete_dataset(self, dataset_id: str) -> None:
        """Delete the dataset with the given ID."""
        pid = self._to_doi(dataset_id)
        resp = self.http.delete(f"/api/datasets/:persistentId/?persistentId={pid}")
        resp.raise_for_status()

    def add_datafile_to_dataset(
        self,
        dataset_id: str,
        file_path: Path,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Upload a file to the specified dataset."""
        metadata = {
            "pid": self._to_doi(dataset_id),
            "filename": file_path.name,
        }

        df = Datafile()
        df.set(metadata)

        if verbose:
            print(df.get())

        resp = self.api.upload_datafile(
            self._to_doi(dataset_id),
            file_path,
            df.json(),
        )
        resp.raise_for_status()
        return resp.json()

    def get_checksum_by_filename(
        self,
        dataset_id: str,
        filename: str,
    ) -> Optional[Tuple[str, str]]:
        """Return (checksum_type, checksum_value) for a file in the dataset, or None."""
        info = self.get_dataset_info(dataset_id)
        files = info["data"]["latestVersion"]["files"]

        for f in files:
            if f.get("label") == filename:
                c = f["dataFile"]["checksum"]
                return c["type"].lower(), c["value"]

        return None

    def get_max_upload_size(self) -> int:
        """Return Dataverse max upload size in bytes.

        If the setting is missing or the endpoint is unavailable,
        fall back to 9 GB.
        """
        DEFAULT_LIMIT = 9 * 10**9  # 9 GB # noqa: N806  # pylint: disable=invalid-name

        try:
            resp = self.http.get("/api/info/settings/:MaxFileUploadSizeInBytes")

            # Some Dataverse installations return 404 for this endpoint
            if resp.status_code == 404:
                return DEFAULT_LIMIT

            resp.raise_for_status()

            data = resp.json().get("data")
            if data is None:
                return DEFAULT_LIMIT

            return int(data)

        except Exception:
            return DEFAULT_LIMIT
