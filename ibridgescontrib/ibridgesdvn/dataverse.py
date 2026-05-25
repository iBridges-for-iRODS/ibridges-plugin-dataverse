"""Dataverse backend for dataset creation, metadata retrieval, and file upload."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import httpx
from pyDataverse.api import NativeApi
from pyDataverse.auth import BearerTokenAuth
from pyDataverse.exceptions import ApiAuthorizationError
from pyDataverse.models import Datafile, Dataset
from pyDataverse.utils import read_file


class Dataverse:
    """
    A clean backend wrapper around Dataverse operations.

    Responsibilities:
    - Authentication
    - Dataset creation
    - Dataset metadata retrieval
    - File upload
    """

    def __init__(self, url: str, token: str) -> None:
        if not token:
            raise ValueError("Dataverse API token cannot be empty.")

        self.url = url.rstrip("/")
        self.token = token

        if not self._token_valid():
            raise ApiAuthorizationError("Dataverse and API token do not match.")

        # pyDataverse client
        self.api = NativeApi(self.url, self.token)

        # httpx client for endpoints not covered by pyDataverse
        self.http = httpx.Client(
            base_url=self.url,
            headers={"X-Dataverse-key": self.token},
            timeout=30.0,
        )

    def _token_valid(self) -> bool:
        """Validate token using BearerTokenAuth."""
        auth = BearerTokenAuth(self.token)
        req = httpx.Request("GET", self.url)
        modified = next(auth.auth_flow(req))
        return modified.headers.get("authorization") == f"Bearer {self.token}"

    def dataverse_exists(self, alias: str) -> bool:
        resp = self.api.get_dataverse(alias)
        return resp.is_success

    def get_dataverse_info(self, alias: str) -> Dict[str, Any]:
        return self.api.get_children(alias)

    def list_dataverse_content(self, alias: str) -> Dict[str, Any]:
        """Use httpx because pyDataverse does not expose this endpoint."""
        resp = self.http.get(f"/api/dataverses/{alias}/contents")
        resp.raise_for_status()
        return resp.json()

    def dataset_exists(self, dataset_id: str) -> bool:
        resp = self.api.get_dataset(f"doi:{dataset_id}")
        return resp.status_code in range(200, 300)

    def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        resp = self.api.get_dataset(f"doi:{dataset_id}")
        resp.raise_for_status()
        return resp.json()

    def create_dataset_with_json(
        self,
        dataverse: str,
        metadata_path: Path,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        if not dataverse:
            raise ValueError("Dataverse name must not be empty.")

        ds = Dataset()
        ds.from_json(read_file(str(metadata_path)))

        if verbose:
            print("Dataset metadata ok:", ds.validate_json())
            print(ds.get())

        if not ds.validate_json():
            raise ValueError("Invalid dataset metadata JSON.")

        resp = self.api.create_dataset(dataverse, ds.json())
        resp.raise_for_status()
        return resp.json()

    def create_dataset(
        self,
        dataverse: str,
        metadata_json: str,
    ) -> Dict[str, Any]:
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

    def add_datafile_to_dataset(
        self,
        dataset_id: str,
        file_path: Path,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        metadata = {
            "pid": f"doi:{dataset_id}",
            "filename": file_path.name,
        }

        df = Datafile()
        df.set(metadata)

        if verbose:
            print(df.get())

        resp = self.api.upload_datafile(
            f"doi:{dataset_id}",
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
        """Return (checksum_type, checksum_value) or None."""
        info = self.get_dataset_info(dataset_id)
        files = info["data"]["latestVersion"]["files"]

        for f in files:
            if f.get("label") == filename:
                c = f["dataFile"]["checksum"]
                return c["type"].lower(), c["value"]

        return None
