"""Create the commands to interact with datasets."""

import ast
import warnings
from pathlib import Path

from ibridges.cli.base import BaseCliCommand
from ibridges.cli.util import parse_remote

from ibridgescontrib.ibridgesdvn.dataverse import Dataverse
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf
from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations


class CliDvnCreateDataset(BaseCliCommand):
    """Subcommand to initialize ibridges."""

    names = ["dv-create-ds"]
    description = "Create a new dataset in a Dataverse collection."
    examples = ["dataverse_id --metajson file_path", 'dataverse_id --metadata "title:my_title;.."']

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument(
            "dataverse_id",
            help="Identifier for the Dataverse where the new dataset will be created.",
            type=str,
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
            help="A string defining the minimal metadata for a dataset separated by ';'.",
            type=str,
            nargs="?",
            default=None,
        )
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        # pylint: disable=R0912
        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn
        cur_token = dvn_conf.get_entry(cur_url)[1]["token"]

        dvn_api = Dataverse(cur_url, cur_token)

        if args.metajson and not args.metajson.is_file():
            parser.error(f"Cannot create dataset. {args.metajson} does not exist.")

        if not dvn_api.dataverse_exists(args.dataverse_id):
            parser.error(f"Cannot create dataset. Dataverse {args.dataverse_id} does not exist.")

        if args.metajson:
            dvn_api.create_dataset_with_json(args.dataverse_id, args.metajson)

        if args.metadata:
            meta_items = args.metadata.split(";")
            title = CliDvnCreateDataset._remove_prefix("title", meta_items)
            if len(title) != 1:
                parser.error(f"Please provide title: 'title:my_title', found {title}")
            title = title[0]
            subject = CliDvnCreateDataset._remove_prefix("subject", meta_items)
            if len(subject) > 1:
                parser.error(f"Please provide subject: 'subject:my_subject', found {subject}")
            elif len(subject) == 1:
                subject = subject[0]
            else:
                subject = None
            authors = CliDvnCreateDataset._remove_prefix("authors", meta_items)
            if len(authors) > 1:
                p = ("[{'authorName': 'LastAuthor1, FirstAuthor1', "
                     "'authorAffiliation': 'AuthorAffiliation1'}, "
                     "{'authorName': 'LastAuthor2, FirstAuthor2', "
                     "'authorAffiliation': 'AuthorAffiliation1'}, "
                     "]")
                parser.error(f"Please provide authors: 'authors:{p}'.")
            elif len(authors) == 1:
                authors = authors[0]
            else:
                authors = None
            contacts = CliDvnCreateDataset._remove_prefix("contacts", meta_items)
            if len(contacts) > 1:
                p = ("[{'datasetContactEmail': 'ContactEmail1@mailinator.com', "
                     "'datasetContactName': 'LastContact1, FirstContact1'},"
                     "{'datasetContactEmail': 'ContactEmail2@mailinator.com', "
                     "'datasetContactName': 'LastContact2, FirstContact2'}]")
                parser.error(f"Please provide authors: 'contacts:{p}'.")
            else:
                contacts = None
            description = CliDvnCreateDataset._remove_prefix("description", meta_items)
            if len(description) > 1:
                p = ("description:[{'dsDescriptionValue': 'DescriptionText'},'"
                     "'dsDescriptionValue': 'DescriptionText2'}]")
                parser.error(f"Please provide authors: 'descriptions:{p}'.")
            else:
                description = None
            dvn_api.create_dataset(args.dataverse_id, title, subject,
                                   CliDvnCreateDataset._cast(authors),
                                   CliDvnCreateDataset._cast(contacts),
                                   CliDvnCreateDataset._cast(description),
                                   verbose=True)


    @classmethod
    def _cast(cls, my_list):
        if not my_list:
            return None
        try:
            return ast.literal_eval(my_list[0])
        except (ValueError, SyntaxError):
            return None

    @classmethod
    def _remove_prefix(cls, prefix, items):
        return [s.removeprefix(prefix+":").strip() for s in items if s.startswith(prefix)]

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

class CliDvnAddFile(BaseCliCommand):
    """Subcommand to add (a) file(s) to a dataset."""

    names = ["dv-add-file"]
    description = "Mark one or more iRODS data objects to be uploaded to a Dataverse dataset."
    examples = ["dataset_name irods:path1 irods:path2"]

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
        ops = DvnOperations()
        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn
        cur_token = dvn_conf.get_entry(cur_url)[1]["token"]
        ops.show()
        dvn_api = Dataverse(cur_url, cur_token)
        if not dvn_api.dataset_exists(args.dataset):
            parser.error(f"Cannot mark data file, {args.dataset} does not exist.")

        for ipath in args.remote_path:
            irods_path = parse_remote(ipath, session)
            if not irods_path.exists():
                warnings.warn(f"{irods_path} does not exist, skip!")
                continue
            if irods_path.collection_exists():
                warnings.warn(f"{irods_path} is not a data object, skip!")
                continue

            ops.add_file(cur_url, args.dataset, str(irods_path))

        ops.show()


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
        ops = DvnOperations()
        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn

        for ipath in args.remote_path:
            irods_path = parse_remote(ipath, session)
            if not irods_path.exists():
                warnings.warn(f"{irods_path} does not exist, skip!")
                continue
            if irods_path.collection_exists():
                warnings.warn(f"{irods_path} is not a data object, skip!")
                continue
            ops.rm_file(cur_url, args.dataset, str(irods_path))

class CliDvnStatus(BaseCliCommand):
    """Summarise the changes to the dataset(s)."""

    names = ["dv-status"]
    description = "List all local changes to the dataset(s)."
    examples = [""]

    @staticmethod
    def run_shell(session, parser, args):
        """Run init is not available for shell."""
        ops = DvnOperations()
        ops.show()


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
