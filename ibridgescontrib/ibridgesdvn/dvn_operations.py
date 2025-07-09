"""Save operations in a file to be executed later."""

import json
import warnings
from pathlib import Path
from pprint import pprint

DVN_OPS_PATH = Path.home() / ".dvn" / "dvn_active_ops_log.json"


class DvnOperations:
    """Store dataverse operations which need to be executed."""

    def __init__(self, ops_log_path: Path = DVN_OPS_PATH):
        """Init with current operations in log file."""
        self.ops_log_path = ops_log_path
        self.ops = self._read_ops_log()
        if self.ops:
            self.validate_ops_format()

    def _read_ops_log(self):
        try:
            with open(self.ops_log_path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError:
            return {}

    def validate_ops_format(self):
        """Validate the format of the ops dictionary.

        {
            dataverse instance1:{
                "add_file": [{"dataset": "ds_id", "irods_paths": ["path1", "path2", ...]}]
            },
            dataverse instance2:{
                ...
            }
        }
        """
        for dataverse, ops in self.ops.items():
            if not isinstance(ops, dict):
                raise ValueError(f"Entry {dataverse} in {DVN_OPS_PATH} needs to be dictionary.")
            if "add_file" in ops:
                if not isinstance(ops["add_file"], list):
                    raise ValueError(f"Entry 'add_file' in {dataverse} needs to be list.")
                for item in ops["add_file"]:
                    if not isinstance(item, dict):
                        raise ValueError(f"Entry 'add_file' in {dataverse} needs to contain dicts.")

    def show(self):
        """Print operations to screen."""
        pprint(self.ops)

    def _get_dataset_ids(self, dataverse_url):
        return [item["dataset"] for item in self.ops[dataverse_url]["add_file"]]

    def _get_paths_for_dataset(self, dataset_id, items):
        for item in items:
            if item["dataset"] == dataset_id:
                return item["irods_paths"]
        return None

    def _add_path_to_dataset(self, dataset_id, new_path, items):
        for item in items:
            if item["dataset"] == dataset_id:
                item["irods_paths"].append(new_path)
                break

    def _remove_path_from_dataset(self, dataset_id, path_to_remove, items):
        for item in items:
            if item["dataset"] == dataset_id:
                if path_to_remove in item.get("irods_paths", []):
                    item["irods_paths"].remove(path_to_remove)

    def add_file(self, dataverse_url: str, dataset_id: str, irods_paths: list):
        """Add file to list."""
        if dataverse_url in self.ops:
            dv_entry = self.ops[dataverse_url]["add_file"]
            if dataset_id in self._get_dataset_ids(dataverse_url):
                registered_paths = self._get_paths_for_dataset(
                    dataset_id, self.ops[dataverse_url]["add_file"]
                )
                for path in irods_paths:
                    if path not in registered_paths:
                        self._add_path_to_dataset(
                            dataset_id, path, self.ops[dataverse_url]["add_file"]
                        )
            else:
                # dataset_id does not exist yet
                new_entry = {"dataset": dataset_id, "irods_paths": irods_paths}
                dv_entry.append(new_entry)

        else:
            # url does not exist
            self.ops[dataverse_url] = {
                "add_file": [{"dataset": dataset_id, "irods_paths": irods_paths}]
            }

        self.validate_ops_format()
        self.save()

    def rm_file(self, dataverse_url: str, dataset_id: str, irods_paths: list):
        """Remove file from the operations."""
        if dataverse_url not in self.ops:
            warnings.warn(f"No operations found for {dataverse_url}. Nothing to do.. Exit.")
            return
        if dataset_id not in self._get_dataset_ids(dataverse_url):
            warnings.warn(f"No operations found for {dataset_id}. Nothing to do.. Exit.")
            return
        registered_paths = self._get_paths_for_dataset(
            dataset_id, self.ops[dataverse_url]["add_file"]
        )

        for path in irods_paths:
            if path in registered_paths:
                self._remove_path_from_dataset(
                    dataset_id, path, self.ops[dataverse_url]["add_file"]
                )
        self.validate_ops_format()
        self.save()

    def save(self):
        """Save the operations object to json."""
        Path(self.ops_log_path).parent.mkdir(exist_ok=True, parents=True)
        with open(self.ops_log_path, "w", encoding="utf-8") as handle:
            json.dump(self.ops, handle, indent=4)
