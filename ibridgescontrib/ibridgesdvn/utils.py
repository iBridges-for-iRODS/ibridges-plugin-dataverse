"""Utils used by Cli and Gui."""

from pathlib import Path


def create_unique_filename(local_dir: Path, filename: str):
    """Create a unique filename for a directory and original filename."""
    counter = 1
    local_path = local_dir / filename
    while local_path.exists():
        extension = filename.split(".")[-1]
        name = filename.split(".")[:-1]
        local_path = local_dir / (name + "_" + str(counter) + extension)
        counter += 1

    return local_path
