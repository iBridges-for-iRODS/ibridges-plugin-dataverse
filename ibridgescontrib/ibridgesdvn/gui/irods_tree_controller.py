"""Build tree."""
from pathlib import PurePath

from ibridges import IrodsPath
from ibridgesgui.irods_tree_model import IrodsTreeModel
from PySide6.QtCore import QModelIndex


class IrodsTreeController:
    """Encapsulates all logic for initializing and expanding the iRODS tree."""

    def __init__(self, session, tree_view):
        """Init."""
        self.session = session
        self.tree_view = tree_view
        self.model = None

    def init_tree(self):
        """Initialize the iRODS tree and expand to the user's home."""
        root = self._irods_root()
        self.model = IrodsTreeModel(self.tree_view, root)

        self.tree_view.setModel(self.model)
        self.tree_view.expanded.connect(self.model.refresh_subtree)

        self.model.init_tree()

        # Expand root
        self.tree_view.expand(self.model.index(0, 0))

        # Expand down to home
        self._expand_to_home()

        # Hide unused columns
        for col in range(1, 6):
            self.tree_view.setColumnHidden(col, True)

    def _irods_root(self):
        """Find the topmost existing iRODS path."""
        lowest = IrodsPath(self.session).absolute()
        while lowest.parent.exists() and str(lowest) != "/":
            lowest = lowest.parent
        return lowest

    def _irods_path_components(self, path):
        """Return list of absolute path components from / to the given path."""
        parts = PurePath(path).parts
        abs_paths = []
        current = ""

        for part in parts:
            if part == "/":
                current = "/"
            else:
                current = f"{current.rstrip('/')}/{part}"
            abs_paths.append(current)

        return abs_paths

    def _expand_to_home(self):
        """Expand the tree down to the user's home directory."""
        components = self._irods_path_components(self.session.home)

        parent_index = QModelIndex()

        for comp in components:
            found = None

            for row in range(self.model.rowCount(parent_index)):
                idx = self.model.index(row, 0, parent_index)
                item_path = self.model.data(idx.sibling(idx.row(), self.model.COL_PATH))

                if item_path == comp:
                    found = idx
                    break

            if found is None:
                return

            self.tree_view.expand(found)
            parent_index = found

        self.tree_view.setCurrentIndex(parent_index)
        self.tree_view.scrollTo(parent_index)
