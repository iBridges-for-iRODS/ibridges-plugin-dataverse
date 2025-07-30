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

def calculate_sha1_checksum(file_path):
    """Calculate the SHA-1 checksum of a file.

    Parameters
    ----------
    file_path:
        Path to the file.

    Returns
    -------
        SHA-1 checksum as a hexadecimal string.

    """
    sha1 = hashlib.sha1()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha1.update(chunk)
        return sha1.hexdigest()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except IOError as e:
        print(f"I/O error: {e}")
        return None
