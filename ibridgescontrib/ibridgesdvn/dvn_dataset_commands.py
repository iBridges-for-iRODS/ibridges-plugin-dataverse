"""Create the commands to interact with datasets."""

from pathlib import Path

from ibridges.cli.base import BaseCliCommand


class CliDvnCreateDataset(BaseCliCommand):
    """Subcommand to initialize ibridges."""

    names = ["dv-create-ds"]
    description = "Create a new dataset in a Dataverse collection."
    examples = ["dataverse_id new_dataset_name"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "dataverse_id",
            help="Identifier for the Dataverse where the new dataset will be created.",
            type=str,
            default=None,
        )

        parser.add_argument(
            "dataset",
            help="The name/id of the new dataset.",
            type=str,
            default=None,
        )

        parser.add_argument(
            "--metajson",
            help="Metadata JSON file, e.g., like dataset.json from pyDataverse's user guide.",
            type=Path,
            nargs="?",
            default=None,
        )

        parser.add_argument(
            "--metadata",
            help="A string defining the minimal metadata for a dataset.",
            type=str,
            nargs="?",
            default=None,
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        print(args)


class CliDvnAddDatasetMeta(BaseCliCommand):
    """Add extra metadata to a dataset."""

    names = ["dv-meta-ds"]
    description = "Add or overwrite metadata of a dataset."
    examples = ["dataset_name"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "dataset",
            help="The name/id of the new dataset.",
            type=str,
            default=None,
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        print(args)


class CliDvnSwitchDataset(BaseCliCommand):
    """Subcommand to switch to another dataset."""

    names = ["dv-switch-ds"]
    description = "Switch to another dataset."
    examples = ["new_dataset_name"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "dataset",
            help="The name/id of the new dataset.",
            type=str,
            default=None,
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        print(args)


class CliDvnAddFile(BaseCliCommand):
    """Subcommand to add (a) file(s) to a dataset."""

    names = ["dv-add-file"]
    description = "Mark one or more iRODS data objects to be uploaded to a Dataverse dataset."
    examples = ["new_dataset_name irods:path1 irods:path2"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "dataset",
            help="The name/id of the new dataset.",
            type=str,
            default=None,
        )
        parser.add_argument(
            "remote_path",
            help="Path to remote iRODS location starting with 'irods:'",
            type=str,
            nargs="+",
        )

        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        print(args)


class CliDvnRmFile(BaseCliCommand):
    """Subcommand to add (a) file(s) to a dataset."""

    names = ["dv-rm-file"]
    description = "Remove one or more iRODS data objects from upload to a Dataverse dataset."
    examples = ["new_dataset_name irods:path1 irods:path2"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "dataset",
            help="The name/id of the new dataset.",
            type=str,
            default=None,
        )
        parser.add_argument(
            "remote_path",
            help="Path to remote iRODS location starting with 'irods:'",
            type=str,
            nargs="+",
        )

        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        print(args)


class CliDvnStatus(BaseCliCommand):
    """Summarise the changes to the dataset(s)."""

    names = ["dv-status"]
    description = "List all local changes to the dataset(s)."
    examples = ["", "dataset_id"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "dataset", help="The name/id of the dataset.", type=str, default=None, nargs="*"
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        print(args)


class CliDvnPush(BaseCliCommand):
    """Push changes of a dataset to the currently configured Dataverse."""

    names = ["dv-push"]
    description = "Push all local changes to the dataverse collection."
    examples = ["dataset_id"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "dataset_id",
            help="The name/id of the dataset to send to dataverse.",
            type=str,
            default=None,
            nargs="*",
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        print(args)
