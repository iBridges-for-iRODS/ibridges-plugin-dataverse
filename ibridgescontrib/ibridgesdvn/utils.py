"""Utils used by CLI and GUI."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional
from typing import Optional, Tuple
from ibridgescontrib.ibridgesdvn.dataverse import Dataverse


def create_unique_filename(local_dir: Path, filename: str) -> Path:
    """Create a unique filename in a directory based on an original filename."""
    local_dir = Path(local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)

    base = Path(filename).stem
    suffix = Path(filename).suffix  # includes the dot, e.g. ".txt"

    candidate = local_dir / (base + suffix)
    counter = 1

    while candidate.exists():
        candidate = local_dir / f"{base}_{counter}{suffix}"
        counter += 1

    return candidate


def calculate_checksum(file_path: Path, alg: str = "sha1") -> Optional[str]:
    """Calculate the checksum of a file.

    Parameters
    ----------
    file_path:
        Path to the file.
    alg:
        Hash algorithm: sha1, sha256, sha512, md5

    Returns
    -------
    Checksum as a hexadecimal string, or None on error.

    """
    file_path = Path(file_path)

    # Normalize algorithm names like "SHA-1" → "sha1"
    alg = alg.lower().replace("-", "")

    algorithms = {
        "sha1": hashlib.sha1,
        "md5": hashlib.md5,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
    }

    if alg not in algorithms:
        raise ValueError(f"Unsupported algorithm: {alg}")

    hasher = algorithms[alg]()

    try:
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except OSError as e:
        print(f"I/O error while reading {file_path}: {e}")
        return None


def ensure_connection(dvn_conf, url: str) -> Tuple[bool, Optional[Dataverse], Optional[str]]:
    """
    Validate URL + token exactly like the CLI does.

    Returns:
        (ok, dv_api, error_message)
        ok: True if connection succeeded
        dv_api: Dataverse instance or None
        error_message: None if ok, otherwise a string
    """
    # 1. Extract token from config
    try:
        entry = dvn_conf.get_entry(url)[1]
    except Exception as exc:
        return False, None, f"Invalid Dataverse entry: {exc}"

    token = entry.get("token", None)
    if not token:
        return False, None, "Token is missing. Please setup connection."

    # 2. Try to construct Dataverse client (CLI-style)
    try:
        dv_api = Dataverse(url, token)
        return True, dv_api, None
    except Exception as exc:
        return False, None, repr(exc)
