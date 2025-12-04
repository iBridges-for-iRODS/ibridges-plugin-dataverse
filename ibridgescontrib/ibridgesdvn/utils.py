"""Utils used by Cli and Gui."""

import hashlib
from pathlib import Path


def create_unique_filename(local_dir: Path, filename: str):
    """Create a unique filename for a directory and original filename."""
    print(local_dir, filename)
    counter = 1
    local_path = local_dir / filename
    while local_path.exists():
        extension = filename.split(".")[-1]
        name = ".".join(filename.split(".")[:-1])
        print(name, extension)
        local_path = local_dir / (name + "_" + str(counter) + extension)
        counter += 1

    return local_path


def calculate_checksum(file_path, alg = "sha1"):
    """Calculate the checksum of a file.

    Parameters
    ----------
    file_path:
        Path to the file.
    alg:
        Hash algorithm: sha1, sha-256, sha-512, md5

    Returns
    -------
        Checksum as a hexadecimal string.

    """
    if alg == "sha1":
        checksum = hashlib.sha1()
    elif alg == "md5":
        checksum = hashlib.md5()
    elif alg == "sha256":
        checksum = hashlib.sha256()
    elif alg == "sha512":
        checksum = hashlib.sha512()
    else:
        raise ValueError(f"Unsupported algorithm: {alg}")
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                checksum.update(chunk)
        return checksum.hexdigest()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except IOError as e:
        print(f"I/O error: {e}")
        return None
