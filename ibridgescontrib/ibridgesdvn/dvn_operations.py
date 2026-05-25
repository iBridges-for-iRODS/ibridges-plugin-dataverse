"""Manage queued Dataverse operations (e.g., pending file uploads)."""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Dict, List, Optional

DVN_OPS_PATH = Path.home() / ".dvn" / "dvn_active_ops_log.json"


class DvnOperations:
    """
    Store Dataverse operations that need to be executed later.

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
        self.ops_log_path = ops_log_path
        self.ops: Dict[str, Dict[str, list]] = self._read_ops_log()
        self._validate_structure()
        self._auto_cleanup()

    def _read_ops_log(self) -> Dict[str, dict]:
        try:
            with self.ops_log_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save(self) -> None:
        self.ops_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ops_log_path.open("w", encoding="utf-8") as f:
            json.dump(self.ops, f, indent=4)

    def _validate_structure(self) -> None:
        for dv_url, dv_ops in self.ops.items():
            if not isinstance(dv_ops, dict):
                raise ValueError(f"Entry for {dv_url} must be a dict.")

            # Ensure keys exist
            dv_ops.setdefault("add_file", [])
            dv_ops.setdefault("created_datasets", [])

            # Validate add_file
            if not isinstance(dv_ops["add_file"], list):
                raise ValueError(f"'add_file' for {dv_url} must be a list.")

            for item in dv_ops["add_file"]:
                if not isinstance(item, dict):
                    raise ValueError(f"Entries in 'add_file' for {dv_url} must be dicts.")
                if "dataset" not in item:
                    raise ValueError(f"Missing 'dataset' key in entry for {dv_url}.")
                if "irods_paths" in item and not isinstance(item["irods_paths"], list):
                    raise ValueError(f"'irods_paths' must be a list in entry for {dv_url}.")

            # Validate created_datasets
            if not isinstance(dv_ops["created_datasets"], list):
                raise ValueError(f"'created_datasets' for {dv_url} must be a list.")

    def _auto_cleanup(self) -> None:
        """
        Automatically remove dataset entries with no pending paths.
        """
        changed = False
        for dv_url, dv_ops in self.ops.items():
            before = len(dv_ops["add_file"])
            dv_ops["add_file"] = [
                entry for entry in dv_ops["add_file"]
                if entry.get("irods_paths")
            ]
            if len(dv_ops["add_file"]) != before:
                changed = True

        if changed:
            self.save()

    def clean_up_datasets(self) -> None:
        """
        Public wrapper to trigger automatic cleanup of stale dataset entries.
        """
        self._auto_cleanup()
        self.save()


    def _ensure_dv_entry(self, dv_url: str) -> Dict[str, list]:
        if dv_url not in self.ops:
            self.ops[dv_url] = {"add_file": [], "created_datasets": []}
        return self.ops[dv_url]

    def _find_dataset_entry(self, dv_url: str, dataset_id: str) -> Optional[dict]:
        for entry in self._ensure_dv_entry(dv_url)["add_file"]:
            if entry["dataset"] == dataset_id:
                return entry
        return None

    def add_file(self, dv_url: str, dataset_id: str, irods_path: str) -> None:
        dv_ops = self._ensure_dv_entry(dv_url)
        ds_entry = self._find_dataset_entry(dv_url, dataset_id)

        if ds_entry:
            paths = ds_entry.setdefault("irods_paths", [])
            if irods_path not in paths:
                paths.append(irods_path)
        else:
            dv_ops["add_file"].append({
                "dataset": dataset_id,
                "irods_paths": [irods_path],
            })

        self._validate_structure()
        self._auto_cleanup()
        self.save()

    def rm_file(self, dv_url: str, dataset_id: str, irods_path: str) -> None:
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

        self._validate_structure()
        self._auto_cleanup()
        self.save()

    def get_paths(self, dv_url: str, dataset_id: str) -> Optional[List[str]]:
        ds_entry = self._find_dataset_entry(dv_url, dataset_id)
        return ds_entry.get("irods_paths") if ds_entry else None

    def register_created_dataset(self, dv_url: str, dataset_id: str) -> None:
        """
        Track newly created datasets so the workflow can auto-push them later.
        """
        dv_ops = self._ensure_dv_entry(dv_url)
        if dataset_id not in dv_ops["created_datasets"]:
            dv_ops["created_datasets"].append(dataset_id)
        self.save()

    def get_created_datasets(self, dv_url: str):
        """
        Return the list of locally tracked draft datasets for this Dataverse.
        """
        dv_ops = self._ensure_dv_entry(dv_url)
        return dv_ops.get("created_datasets", [])

    def flush_dataset(self, dv_url: str, dataset_id: str) -> None:
        """
        Remove all operations for a dataset after a successful push.
        """
        dv_ops = self._ensure_dv_entry(dv_url)
        dv_ops["add_file"] = [
            entry for entry in dv_ops["add_file"]
            if entry["dataset"] != dataset_id
        ]
        if dataset_id in dv_ops["created_datasets"]:
            dv_ops["created_datasets"].remove(dataset_id)

        self._auto_cleanup()
        self.save()

    def force_delete_dataset(self, dv_url: str, dataset_id: str, dvn_api) -> None:
        """
        Delete a dataset from Dataverse (if possible) and remove all local tracking.
        """
        # Try deleting from Dataverse
        try:
            dvn_api.delete_dataset(dataset_id)
            self.flush_dataset(dv_url, dataset_id)
        except Exception:
            # If deletion fails (e.g. dataset already gone), continue cleanup
            pass

    def show(self, dvn_api=None) -> None:
        """
        Pretty-print pending upload operations with dataset status.
        """
        if not self.ops:
            print("No pending Dataverse operations.")
            return
    
        for dv_url, dv_ops in self.ops.items():
            print(f"\nDataverse: {dv_url}")
            print("-" * (len(dv_url) + 11))
    
            entries = dv_ops.get("add_file", [])
    
            if not entries:
                print("  No pending uploads.")
                continue
    
            print("  Pending uploads:")
            for entry in entries:
                ds = entry["dataset"].strip()
                paths = entry.get("irods_paths", [])
                if dvn_api:
                    try:
                        state = dvn_api.get_dataset_state(ds)
                    except Exception:
                        state = "UNKNOWN"
                else:
                    state = "UNKNOWN"
    
                print(f"    • Dataset {ds} [{state}]")
                for p in paths:
                    print(f"        - {p}")

    def show_created_datasets(self, dvn_api=None) -> None:
        """
        Pretty-print created datasets with their Dataverse status.
        """
        print("\nDatasets:")
        print("--------------------------------")
    
        found_any = False
    
        for dv_url, dv_ops in self.ops.items():
            created = dv_ops.get("created_datasets", [])
            if not created:
                continue
    
            found_any = True
            print(f"\nDataverse: {dv_url}")
    
            for ds in sorted(set(created)):
                if dvn_api:
                    try:
                        state = dvn_api.get_dataset_state(ds)
                    except Exception:
                        state = "UNKNOWN"
                else:
                    state = "UNKNOWN"
    
                print(f"  • {ds:<30} [{state}]")
    
        if not found_any:
            print("No draft datasets.")


    def get_created_datasets(self, dv_url: str) -> list[str]:
        """
        Return a sorted list of created dataset IDs for a Dataverse instance.
        """
        dv_ops = self._ensure_dv_entry(dv_url)
        return sorted(set(dv_ops.get("created_datasets", [])))

    def delete_created_datasets(self, dv_url: str, dataset_ids: list[str]) -> None:
        """
        Delete one or more dataset IDs from the created_datasets list.
    
        Parameters
        ----------
        dv_url : str
            Dataverse instance URL.
        dataset_ids : list[str]
            One or more dataset IDs to remove.
        """
        dv_ops = self._ensure_dv_entry(dv_url)
        existing = dv_ops.get("created_datasets", [])
    
        # Remove only those that exist
        dv_ops["created_datasets"] = [
            ds for ds in existing if ds not in dataset_ids
        ]
    
        self.save()

    def remove_published_drafts(self, dv_url: str, dvn_api) -> None:
        """
        Remove draft datasets that have been published on Dataverse.
        """
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
        self.save()
