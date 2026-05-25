from ibridgescontrib.ibridgesdvn.dvn_operations import DvnOperations
from ibridgescontrib.ibridgesdvn.dvn_config import DVNConf
from ibridgescontrib.ibridgesdvn.dataverse import Dataverse

class CliDvnDeleteDataset(BaseCliCommand):
    names = ["dv-delete-ds"]
    description = "Delete a draft dataset from Dataverse."
    examples = ["dataset_id"]

    @classmethod
    def _mod_parser(cls, parser):
        parser.add_argument("dataset_id", type=str)
        return parser

    @staticmethod
    def run_shell(session, parser, args):
        dvn_conf = DVNConf(parser)
        cur_url = dvn_conf.cur_dvn
        token = dvn_conf.get_entry(cur_url)[1]["token"]

        dvn_api = Dataverse(cur_url, token)
        ops = DvnOperations()

        dataset_id = args.dataset_id.strip()
        if dataset_id.startswith("doi:"):
            dataset_id = dataset_id[4:]

        # 1. Check existence
        try:
            state = dvn_api.get_dataset_state(dataset_id)
        except Exception:
            print(f"Warning: Dataset {dataset_id} does not exist in Dataverse.")
            return

        # 2. Refuse deletion if not DRAFT
        if state != "DRAFT":
            parser.error(
                f"Dataset {dataset_id} is in state {state} and cannot be deleted. "
                "Only DRAFT datasets may be deleted."
            )

        # 3. Refuse deletion if dataset is not empty
        info = dvn_api.get_dataset_info(dataset_id)
        files = info["data"]["latestVersion"].get("files", [])

        if files:
            parser.error(
                f"Dataset {dataset_id} is not empty ({len(files)} files). "
                "Refusing deletion."
            )

        # 4. Delete from Dataverse
        dvn_api.delete_dataset(dataset_id)
        print(f"Deleted dataset {dataset_id} from Dataverse.")

        # 5. Remove from local tracking
        ops.delete_created_datasets(cur_url, [dataset_id])
        print(f"Removed dataset {dataset_id} from local draft list.")
