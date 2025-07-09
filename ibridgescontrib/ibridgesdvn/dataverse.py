"""Dataverse functionality for creating a draft."""

from pathlib import Path

from httpx import Client, Request
from httpx._exceptions import HTTPError
from pyDataverse.api import NativeApi
from pyDataverse.auth import BearerTokenAuth
from pyDataverse.exceptions import ApiAuthorizationError
from pyDataverse.models import Datafile, Dataset
from pyDataverse.utils import read_file

from ibridgescontrib.ibridgesdvn.json_templates import dataset_json


class Dataverse:
    """A utility class to interact with a Dataverse instance using the provided URL and API token.

    This class supports authentication, dataset management, and metadata retrieval.
    """

    def __init__(self, url: str, token: str):
        """Initialise the DataverseOperations instance.

        Args:
        ----
            url (str): The base URL of the Dataverse instance.
            token (str): The API token used for authentication.

        Raises:
        ------
            ValueError: If the API token is not provided.
            ApiAuthorizationError: If the token does not successfully authenticate.

        """
        self.dvn_url = url
        self.dvn_token = token

        if self.dvn_token is None:
            raise ValueError("Dataverse API token cannot be empty.")

        if self.user_authenticated():
            self.api = NativeApi(self.dvn_url, self.dvn_token)
        else:
            raise ApiAuthorizationError("Dataverse and API token do not match.")

    def user_authenticated(self) -> True:
        """Verify if the user token is valid for the Dataverse instance.

        Returns:
        -------
            bool: True if the token is valid and authentication succeeds.

        Note:
        ----
            This method performs a basic request with the Bearer token to check authorization.

        """
        auth = BearerTokenAuth(self.dvn_token)
        request = Request("GET", self.dvn_url)
        modified_request = next(auth.auth_flow(request))
        return modified_request.headers["authorization"] == "Bearer " + self.dvn_token

    def get_dataverse_info(self, dataverse):
        """Retrieve the children (datasets and sub-dataverses) of a specified Dataverse.

        Args:
        ----
            dataverse (str): The alias or identifier of the Dataverse.

        Returns:
        -------
            dict: The response containing child items of the Dataverse.

        """
        return self.api.get_children(dataverse)

    def dataverse_exists(self, dataverse: str):
        """Check whether a specified Dataverse exists.

        Args:
        ----
            dataverse (str): The alias or identifier of the Dataverse.

        Returns:
        -------
            bool: True if the Dataverse exists; False otherwise.

        """
        answer = self.api.get_dataverse(dataverse)
        return answer.is_success

    def list_dataverse_content(self, dataverse: str) -> dict:
        """Retrieve the list of datasets and sub-dataverses contained within a specified Dataverse.

        Args:
        ----
            dataverse (str): The alias or identifier of the Dataverse to query.

        Returns:
        -------
            dict: A dictionary representing the JSON response from the Dataverse API,
                  typically including datasets and nested dataverses.

        Raises:
        ------
            HTTPError: If the API response status code is not 200 (i.e., request failed).

        """
        url = f"https://demo.dataverse.nl/api/dataverses/{dataverse}/contents"
        headers = {"X-Dataverse-key": self.dvn_token}

        request = Request("GET", url, headers=headers)
        with Client() as client:
            response = client.send(request)

        if response.status_code in range(200, 300):
            return response.json()
        raise HTTPError(f"{response.status_code}, {response.reason_phrase}")

    def get_dataset_info(self, data_id: str):
        """Retrieve metadata and information for a dataset using its DOI identifier.

        Args:
        ----
            data_id (str): The dataset identifier (excluding the 'doi:' prefix).

        Returns:
        -------
            dict: The JSON response containing dataset metadata and details.

        Raises:
        ------
            HTTPError: If the API response status code is not 200 (successful).

        """
        response = self.api.get_dataset(f"doi:{data_id}")
        if response.status_code in range(200, 300):
            return response.json()
        raise HTTPError(f"{response.status_code}, {response.reason_phrase}")

    def create_dataset_with_json(self, dataverse: str, metadata: Path, verbose: bool = False):
        """Create a new dataset from a json metadata file.

        Parameters
        ----------
        dataverse:
            The name of the Dataverse Collection where the dataset will be created.
        metadata:
            The path to a valid Dataverse Dataset metadata file.
        verbose:
            Print summary if True.

        """
        if dataverse is None:
            raise ValueError("Dataverse name must not be empty.")

        ds = Dataset()
        ds.from_json(read_file(str(metadata)))

        if verbose:
            print("Dataset metadata ok:", ds.validate_json())
            print(ds.get())

        if not ds.validate_json():
            raise ValueError("Something is wrong with the dataset's metadata.")

        response = self.api.create_dataset(dataverse, ds.json())

        if response.status_code not in range(200, 300):
            raise HTTPError(f"{response.status_code}, {response.reason_phrase}")

        return response


    def create_dataset(
        self,
        dataverse: str,
        title: str,
        subject: str=None,
        authors: list[dict]=None,
        contacts: list[dict]=None,
        description: list[dict]=None,
        verbose: bool = True,
    ):  # pylint: disable=R0913, R0917
        """Create a new dataset in a specified Dataverse repository.

        Parameters
        ----------
        dataverse:
            The name of the Dataverse Collection where the dataset will be created.
        title:
            The title of the dataset.
        subject:
            The subject area or field of the dataset.
        authors:
            A list of dictionaries containing author details.
            [{'authorName': 'LastAuthor1, FirstAuthor1',
                'authorAffiliation': 'AuthorAffiliation1'},
             {'authorName': 'LastAuthor2, FirstAuthor2',
                'authorAffiliation': 'AuthorAffiliation2'}]
        contacts:
            A list of contacts.
            [{'datasetContactEmail': 'ContactEmail1@mailinator.com',
              'datasetContactName': 'LastContact1, FirstContact1'},
             {'datasetContactEmail': 'ContactEmail2@mailinator.com',
              'datasetContactName': 'LastContact2, FirstContact2'}
              ]
        description:
            A list of descriptions providing information about the dataset.
            [{'dsDescriptionValue': 'DescriptionText'},
             {'dsDescriptionValue': 'DescriptionText2'}]
        verbose:
            If True, prints dataset details for debugging. Defaults to True.

        Raises
        ------
                ValueError: If any of the required parameters are missing or empty
                    (e.g., dataverse, title, subject, authors, contacts).
                HTTPError: If the response from the API is not successful
                    (i.e., status code is not 200).

        Returns
        -------
            None: The function creates the dataset but does not return any value.

        """
        if dataverse is None:
            raise ValueError("Dataverse name must not be empty.")
        if title is None:
            raise ValueError("Title must not be empty.")

        ds = Dataset()
        ds.from_json(dataset_json)
        ds.set({"title": title})
        if subject:
            ds.set({"subject": subject})
        if authors:
            ds.set({"author": authors})
        if contacts:
            ds.set({"datasetContact": contacts})
        if description:
            ds.set({"dsDescription": description})

        if verbose:
            print("Dataset metadata ok:", ds.validate_json())
            print(ds.get())


        if not ds.validate_json():
            raise ValueError("Something is wrong with the dataset's metadata.")

        response = self.api.create_dataset(dataverse, ds.json())

        if response.status_code not in range(200, 300):
            raise HTTPError(f"{response.status_code}, {response.reason_phrase}")

    def add_datafile_to_dataset(self, dataset_id: str, file_path: Path, verbose: bool = True):
        """Upload a data file to a specific dataset.

        Parameters
        ----------
        dataset_id:
           The ID of the dataset to which the data file will be uploaded.
        file_path:
           The file path of the data file to be uploaded.
        verbose:
           If True, prints additional details for debugging. Defaults to True.

        Raises
        ------
            HTTPError: If the response status code is not 200,
                       an HTTPError is raised with the status code and reason.

        Returns
        -------
            None: The function uploads the file and does not return any value.

        """
        data_metadata = {"pid": "doi:dataset_id", "filename": file_path.name}

        df = Datafile()
        df.set(data_metadata)

        if verbose:
            print(df.get())

        response = self.api.upload_datafile(f"doi:{dataset_id}", file_path, df.json())

        if response.status_code in range(200, 300):
            raise HTTPError(f"{response.status_code}, {response.reason_phrase}")
