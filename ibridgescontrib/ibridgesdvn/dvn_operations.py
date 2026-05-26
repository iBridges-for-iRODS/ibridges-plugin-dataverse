"""Manage queued Dataverse operations (e.g., pending file uploads)."""

from __future__ import annotations

import json
import shutil
import warnings
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Optional
import httpx

from ibridges import IrodsPath, download

from ibridgescontrib.ibridgesdvn.dataverse import Dataverse
from ibridgescontrib.ibridgesdvn.dvn_config import DVN_CONFIG_FP, DVNConf
from ibridgescontrib.ibridgesdvn.utils import calculate_checksum, create_unique_filename

DVN_OPS_PATH = Path.home() / ".dvn" / "dvn_active_ops_log.json"
TEMP_DIR = Path.home() / ".dvn" / "data"


class DvnOperations:
    """Store Dataverse operations that need to be executed later.

    Structure:
    {
        "https://demo.dataverse.org": {
            "add_file": [
                {"dataset": "123", "irods_paths": ["a", "b"]},
                {"dataset": "456", "irods_paths": ["c"]}
            ],
            "created_datasets": ["123", "456"]
        }
    }
    """

    def __init__(self, ops_log_path: Path = DVN_OPS_PATH):
        """Init."""
        self.ops_log_path = ops_log_path
        self.ops: Dict[str, Dict[str, list]] = self._read_ops_log()
        self._validate_structure()
        self._auto_cleanup()

    def _validate_dv(self, dv_url: str, parser=None):
        """Validate that the Dataverse URL exists, is reachable, and has a valid token."""
        dvn_conf = DVNConf(DVN_CONFIG_FP, parser)
        try:
            url, entry = dvn_conf.get_entry(dv_url)
        except KeyError as exc:
            raise RuntimeError(f"No Dataverse configuration found for '{dv_url}'.") from exc

        if not dvn_conf.is_valid_url(url):
            raise RuntimeError(f"Invalid Dataverse URL: {url}")

        token = entry.get("token")
        if not token:
            raise RuntimeError(f"No API token configured for {url}. Use 'dv-init' first.")

        try:
            resp = httpx.get(
                f"{url}/api/users/:me",
                headers={"X-Dataverse-key": token},
                timeout=3.0,
            )
            if resp.status_code != 200:
                raise RuntimeError(
                    f"Invalid API token for {url}. Use 'dv-init' to set a valid token."
                )
        except Exception as exc:
            raise RuntimeError(f"Dataverse at {url} is unreachable.") from exc

        return url, token

    def _read_ops_log(self) -> Dict[str, dict]:
        try:
            with self.ops_log_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save(self) -> None:
        self.ops_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ops_log_path.open("w", encoding="utf-8") as f:
            json.dump(self.ops, f, indent=4)

    def _commit(self) -> None:
        """Validate, cleanup, and save."""
        self._validate_structure()
        self._auto_cleanup()
        self._save()

    def _validate_structure(self) -> None:
        for dv_url, dv_ops in self.ops.items():
            if not isinstance(dv_ops, dict):
                raise ValueError(f"Entry for {dv_url} must be a dict.")

            dv_ops.setdefault("add_file", [])
            dv_ops.setdefault("created_datasets", [])

            if not isinstance(dv_ops["add_file"], list):
                raise ValueError(f"'add_file' for {dv_url} must be a list.")
            if not isinstance(dv_ops["created_datasets"], list):
                raise ValueError(f"'created_datasets' for {dv_url} must be a list.")

    def _auto_cleanup(self) -> None:
        """Automatically remove empty upload entries and orphaned structures."""
        changed = False

        for _, dv_ops in self.ops.items():
            # 1. Remove add_file entries with no paths
            before = len(dv_ops["add_file"])
            dv_ops["add_file"] = [entry for entry in dv_ops["add_file"] if entry.get("irods_paths")]
            if len(dv_ops["add_file"]) != before:
                changed = True

            # 2. Remove duplicate dataset IDs in created_datasets
            before = len(dv_ops["created_datasets"])
            dv_ops["created_datasets"] = list(sorted(set(dv_ops["created_datasets"])))
            if len(dv_ops["created_datasets"]) != before:
                changed = True

        if changed:
            self._save()

    def clean_up_datasets(self, dv_url: str, parser=None) -> None:
        """Manually trigger full cleanup including Dataverse checks."""
        api = self._get_api(dv_url, parser)
        dv_ops = self._ensure_dv_entry(dv_url)

        cleaned = []
        for ds in dv_ops.get("created_datasets", []):
            try:
                if api.dataset_exists(ds) and not api.is_dataset_published(ds):
                    cleaned.append(ds)
            except Exception:
                cleaned.append(ds)
        dv_ops["created_datasets"] = cleaned

        cleaned_add = []
        for entry in dv_ops.get("add_file", []):
            ds = entry.get("dataset")
            try:
                if api.dataset_exists(ds):
                    cleaned_add.append(entry)
            except Exception:
                pass
        dv_ops["add_file"] = cleaned_add

        self._auto_cleanup()

        self._save()

    def _ensure_dv_entry(self, dv_url: str) -> Dict[str, list]:
        if dv_url not in self.ops:
            self.ops[dv_url] = {"add_file": [], "created_datasets": []}
        return self.ops[dv_url]

    def _find_dataset_entry(self, dv_url: str, dataset_id: str) -> Optional[dict]:
        for entry in self._ensure_dv_entry(dv_url)["add_file"]:
            if entry["dataset"] == dataset_id:
                return entry
        return None

    @contextmanager
    def _temp_dir(self):
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        try:
            yield TEMP_DIR
        finally:
            shutil.rmtree(TEMP_DIR, ignore_errors=True)

    def _get_api(self, dv_url: str, parser=None) -> Dataverse:
        """Build a Dataverse API client from config."""
        url, token = self._validate_dv(dv_url, parser)
        return Dataverse(url, token)

    def _file_too_large(self, api: Dataverse, size: int) -> bool:
        """Return True if size exceeds Dataverse max upload size."""
        try:
            max_size = api.get_max_upload_size()
            return max_size > 0 and size > max_size  # pylint: disable=chained-comparison
        except Exception:
            # Fail-open: if we can't read the setting, don't block upload.
            return False

    def add_file(self, dv_url: str, dataset_id: str, irods_path: str) -> None:
        """Stage an iRODS path for upload to a dataset."""
        dv_ops = self._ensure_dv_entry(dv_url)
        ds_entry = self._find_dataset_entry(dv_url, dataset_id)

        if ds_entry:
            paths = ds_entry.setdefault("irods_paths", [])
            if irods_path not in paths:
                paths.append(irods_path)
        else:
            dv_ops["add_file"].append(
                {
                    "dataset": dataset_id,
                    "irods_paths": [irods_path],
                }
            )

        self._commit()

    def rm_file(self, dv_url: str, dataset_id: str, irods_path: str) -> None:
        """Remove a staged iRODS path from a dataset."""
        if dv_url not in self.ops:
            warnings.warn(f"No operations found for {dv_url}.")
            return

        ds_entry = self._find_dataset_entry(dv_url, dataset_id)
        if not ds_entry:
            warnings.warn(f"No operations found for dataset {dataset_id}.")
            return

        paths = ds_entry.get("irods_paths", [])
        if irods_path in paths:
            paths.remove(irods_path)

        self._commit()

    def get_paths(self, dv_url: str, dataset_id: str) -> Optional[List[str]]:
        """Return staged iRODS paths for a dataset, or None."""
        ds_entry = self._find_dataset_entry(dv_url, dataset_id)
        return ds_entry.get("irods_paths") if ds_entry else None

    def register_created_dataset(self, dv_url: str, dataset_id: str) -> None:
        """Track newly created datasets so the workflow can auto-push them later."""
        dv_ops = self._ensure_dv_entry(dv_url)
        if dataset_id not in dv_ops["created_datasets"]:
            dv_ops["created_datasets"].append(dataset_id)
        self._commit()

    def get_created_datasets(self, dv_url: str) -> list[str]:
        """Return a sorted list of created dataset IDs for a Dataverse instance."""
        dv_ops = self._ensure_dv_entry(dv_url)
        return sorted(set(dv_ops.get("created_datasets", [])))

    def delete_created_datasets(self, dv_url: str, dataset_ids: list[str]) -> None:
        """Delete one or more dataset IDs from the created_datasets list."""
        dv_ops = self._ensure_dv_entry(dv_url)
        existing = dv_ops.get("created_datasets", [])
        dv_ops["created_datasets"] = [ds for ds in existing if ds not in dataset_ids]
        self._commit()

    def remove_published_drafts(self, dv_url: str, dvn_api: Dataverse) -> None:
        """Remove draft datasets that have been published on Dataverse."""
        dv_ops = self._ensure_dv_entry(dv_url)
        drafts = dv_ops.get("created_datasets", [])

        still_drafts = []
        for ds in drafts:
            try:
                if not dvn_api.is_dataset_published(ds):
                    still_drafts.append(ds)
            except Exception:
                # If dataset lookup fails, keep it as draft
                still_drafts.append(ds)

        dv_ops["created_datasets"] = still_drafts
        self._commit()

    # pylint: disable=too-many-positional-arguments
    def create_dataset_from_file(
        self,
        dv_url: str,
        dataverse_alias: str,
        metadata_path: Path,
        parser=None,
        verbose: bool = False,
    ) -> str:
        """Create a dataset from a JSON file and register it as draft."""
        api = self._get_api(dv_url, parser)
        result = api.create_dataset_from_file(dataverse_alias, metadata_path, verbose=verbose)
        pid = result["data"]["persistentId"].replace("doi:", "")
        self.register_created_dataset(dv_url, pid)
        return pid

    def create_dataset_interactive(
        self,
        dv_url: str,
        dataverse_alias: str,
        parser=None,
    ) -> str:
        """Create a dataset by asking for minimal metadata on the command line."""
        api = self._get_api(dv_url, parser)

        title = input("Title: ").strip()
        author = input("Author: ").strip()
        description = input("Description: ").strip()

        # This is intentionally minimal; you can expand to full Dataverse JSON.
        metadata = {
            "datasetVersion": {
                "metadataBlocks": {
                    "citation": {
                        "fields": [
                            {"typeName": "title", "value": title, "typeClass": "primitive"},
                            {
                                "typeName": "author",
                                "typeClass": "compound",
                                "value": [
                                    {
                                        "authorName": {
                                            "typeName": "authorName",
                                            "typeClass": "primitive",
                                            "value": author,
                                        }
                                    }
                                ],
                            },
                            {
                                "typeName": "dsDescription",
                                "typeClass": "compound",
                                "value": [
                                    {
                                        "dsDescriptionValue": {
                                            "typeName": "dsDescriptionValue",
                                            "typeClass": "primitive",
                                            "value": description,
                                        }
                                    }
                                ],
                            },
                        ],
                    },
                },
            },
        }

        metadata_json = json.dumps(metadata)
        result = api.create_dataset_from_json(dataverse_alias, metadata_json)
        pid = result["data"]["persistentId"].replace("doi:", "")
        self.register_created_dataset(dv_url, pid)
        return pid

    # pylint: disable=too-many-positional-arguments, too-many-locals
    def push_dataset(
        self,
        session,
        dv_url: str,
        dataset_id: str,
        check_checksum: bool = True,
        parser=None,
    ) -> None:
        """Push all staged files for a dataset to Dataverse."""
        api = self._get_api(dv_url, parser)

        if not api.dataset_exists(dataset_id):
            raise ValueError(f"Dataset {dataset_id} does not exist.")

        # make copy of paths to loop over and adjust  during loop
        paths = list(self.get_paths(dv_url, dataset_id))
        if not paths:
            print("No files staged for upload.")
            return

        with self._temp_dir() as tmp:
            for p in paths:
                print("STAGED PATHS:", paths)
                ipath = IrodsPath(session, p)

                if not ipath.dataobject_exists():
                    warnings.warn(f"{ipath} does not exist.")
                    continue

                # File size check before download
                try:
                    irods_size = ipath.size()
                except Exception:
                    irods_size = 0

                if irods_size and self._file_too_large(api, irods_size):
                    warnings.warn(f"Skipping {p}: file size {irods_size} exceeds Dataverse limit.")
                    continue

                local_path = create_unique_filename(tmp, ipath.name)
                download(ipath, local_path, overwrite=True)

                api.add_datafile_to_dataset(dataset_id, local_path)

                if check_checksum:
                    checksum_info = api.get_checksum_by_filename(dataset_id, local_path.name)
                    if checksum_info is not None:
                        alg, dvn_checksum = checksum_info
                        local_checksum = calculate_checksum(local_path, alg=alg)
                        if local_checksum != dvn_checksum:
                            warnings.warn(f"Checksum mismatch for {local_path.name}")
                    else:
                        warnings.warn(f"No checksum info found for {local_path.name}")

                self.rm_file(dv_url, dataset_id, p)
                try:
                    local_path.unlink()
                except FileNotFoundError:
                    pass

        # If all files uploaded, flush dataset
        self.flush_dataset(dv_url, dataset_id)

        # Remove from drafts if published
        if api.is_dataset_published(dataset_id):
            self.delete_created_datasets(dv_url, [dataset_id])

    def flush_dataset(self, dv_url: str, dataset_id: str) -> None:
        """Remove all operations for a dataset after a successful push."""
        dv_ops = self._ensure_dv_entry(dv_url)
        dv_ops["add_file"] = [
            entry for entry in dv_ops["add_file"] if entry["dataset"] != dataset_id
        ]

        self._commit()

    def force_delete_dataset(self, dv_url: str, dataset_id: str, dvn_api: Dataverse) -> None:
        """Delete a dataset from Dataverse (if possible) and remove all local tracking."""
        try:
            dvn_api.delete_dataset(dataset_id)
        except Exception:
            # If deletion fails (e.g. dataset already gone), continue cleanup
            pass
        self.flush_dataset(dv_url, dataset_id)
        self.delete_created_datasets(dv_url, [dataset_id])

    def show_status(self, dv_url: str, dvn_api: Dataverse) -> None:
        """Pretty-print pending upload operations and draft datasets with status."""
        dv_ops = self._ensure_dv_entry(dv_url)

        print(f"\nDataverse: {dv_url}")
        print("--------------------------------")

        entries = dv_ops.get("add_file", [])
        drafts = dv_ops.get("created_datasets", [])

        if not entries and not drafts:
            print("No pending Dataverse operations or draft datasets.")
            return

        if entries:
            print("\nPending uploads:")
            for entry in entries:
                ds = entry["dataset"].strip()
                paths = entry.get("irods_paths", [])
                try:
                    state = dvn_api.get_dataset_state(ds)
                except Exception:
                    state = "UNKNOWN"

                print(f"  • Dataset {ds} [{state}]")
                for p in paths:
                    print(f"      - {p}")
        else:
            print("\nNo pending uploads.")

        if drafts:
            print("\nDraft datasets:")
            for ds in sorted(set(drafts)):
                try:
                    state = dvn_api.get_dataset_state(ds)
                except Exception:
                    state = "UNKNOWN"
                print(f"  • {ds:<30} [{state}]")
        else:
            print("\nNo draft datasets.")
