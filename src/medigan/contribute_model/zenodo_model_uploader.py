# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""Zenodo Model uploader class that uploads models to medigan associated data storage on Zenodo

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""

from __future__ import absolute_import

import json
import logging
import shutil
from pathlib import Path

import requests

from ..constants import (
    CONFIG_FILE_KEY_DESCRIPTION,
    CONFIG_FILE_KEY_SELECTION,
    CONFIG_FILE_KEY_TAGS,
    ZENODO_API_URL,
    ZENODO_GENERIC_MODEL_DESCRIPTION,
    ZENODO_HEADERS,
    ZENODO_LINE_BREAK,
)
from .base_model_uploader import BaseModelUploader


class ZenodoModelUploader(BaseModelUploader):
    """`ZenodoModelUploader` class: Uploads a user's model via API to Zenodo, here it is permanently stored with DOI.

    Parameters
    ----------
    model_id: str
        The generative model's unique id
    access_token: str
        a personal access token in Zenodo linked to a user account for authentication

    Attributes
    ----------
    model_id: str
        The generative model's unique id
    access_token: str
        a personal access token in Zenodo linked to a user account for authentication
    """

    def __init__(
        self,
        model_id,
        access_token,
    ):
        self.model_id = model_id
        self.params = {"access_token": access_token}

    ############################ UPLOAD ############################
    def create_upload_description(
        self, metadata: dict, model_description: str = ""
    ) -> str:
        """ Create a string containing the textual description that will accompany the upload model files.

        The string contains tags and a text retrieved from the description subsection of the model metadata.

        Parameters
        ----------
        metadata: dict
            The model's corresponding metadata
        model_description: str
            the model_description that will appear on the corresponding Zenodo model upload homepage

        Returns
        -------
        str
            Returns the textual description of the model upload
        """

        try:
            tags = f"{ZENODO_LINE_BREAK} Tags: {metadata[self.model_id][CONFIG_FILE_KEY_SELECTION][CONFIG_FILE_KEY_TAGS]}"
        except:
            tags = ""
        try:
            description_from_config = f"{ZENODO_LINE_BREAK} Description from model config: {json.dumps(self.metadata[self.model_id][CONFIG_FILE_KEY_DESCRIPTION])}"
        except:
            description_from_config = ""

        return f"{model_description} {ZENODO_LINE_BREAK} Model: {self.model_id}. {ZENODO_LINE_BREAK} Upload via: API {tags} {ZENODO_LINE_BREAK} {ZENODO_GENERIC_MODEL_DESCRIPTION} {description_from_config}"


    def create_upload_json_data(
        self, creator_name: str, creator_affiliation: str, description: str = ""
    ) -> dict:
        """ Create some descriptive data in dict format to be uploaded and stored alongside the model files.

        Parameters
        ----------
        creator_name: str
            the creator name that will appear on the corresponding Zenodo model upload homepage
        creator_affiliation: str
            the creator affiliation that will appear on the corresponding Zenodo model upload homepage
        description: str
            the model_description that will appear on the corresponding Zenodo model upload homepage

        Returns
        -------
        dict
            Returns the descriptive data in dictionary structure describing the model upload.
        """

        return {
            "metadata": {
                "title": f"{self.model_id}",
                "upload_type": "software",
                "description": description,
                "creators": [
                    {
                        "name": f"{creator_name}",
                        "affiliation": f"{creator_affiliation}",
                    }
                ],
            }
        }

    def locate_or_create_model_zip_file(self, package_path: str, package_name: str) -> (str, str):
        """ If not possible to locate, create a zipped python package of the model.

        Parameters
        ----------
        package_path: str
            Path as string to the generative model's python package containing an `__init__.py` file
        package_name: str
            Name of the model's python package i.e. the name of the model's zip file and unzipped package folder

        Returns
        -------
        tuple
            Returns a tuple containing two strings: The `filename` and the `file_path` of and to the zipped python package
        """

        # Check if zip file already exists
        if not (Path(package_path).is_file() and package_path.endswith(".zip")):
            # Create a zip archive for the model in the parent of the model root folder
            root_dir = str(Path(package_path).parent)
            filename = shutil.make_archive(
                base_name=root_dir + "/" + package_name,
                format="zip",
                base_dir=package_path,
                root_dir=root_dir,
            )
            file_path = root_dir + "/" + str(Path(filename).name)
        else:
            filename = Path(package_path).name
            file_path = package_path

        return filename, file_path


    def empty_upload(self) -> dict:
        """ Upload an empty placeholder entry to Zenodo as is required to retrieve a `deposition_id` and `bucket_url`.

        deposition_id and bucket_url aare needed for file upload and publishing in the subsequent upload steps.

        Returns
        -------
        dict
            Returns the response retrieved via the Zenodo API
        """

        r = requests.post(
            ZENODO_API_URL,
            params=self.params,
            json={},
            headers=ZENODO_HEADERS,
        )
        if not r.status_code == 201:
            raise Exception(
                f"{self.model_id}: Error ({r.status_code}!=201) during Zenodo upload (step 1: creating empty upload template): {r.json()}"
            )
        return r


    def upload(self, file_path: str, filename: str, bucket_url: str) -> dict:
        """ Upload a file to Zenodo entry of the uploaded model files.

        Parameters
        ----------
        file_path: str
            The path of the file that is uploaded to Zenodo
        filename: str
            The name of the file that is uploaded to Zenodo
        bucket_url: str
            The bucket url used in the PUT request to upload the data file.

        Returns
        -------
        dict
            Returns the response retrieved via the Zenodo API
        """

        with open(file_path, "rb") as fp:
            r = requests.put(
                "%s/%s" % (bucket_url, filename),
                data=fp,
                params=self.params,
            )

        if not r.status_code == 200:
            raise Exception(
                f"{self.model_id}: Error ({r.status_code}!=200) during Zenodo upload (step 2: uploading model as zip file): {r.json()}"
            )
        return r

    def upload_descriptive_data(self, deposition_id: str, data: dict) -> dict:
        """ Upload textual descriptive data to be associated and added to the Zenodo entry of the uploaded model files.

        Parameters
        ----------
        deposition_id: str
            The deposition id assigned by Zenodo to the uploaded model file
        data: dict
            The descriptive information that will to be uploaded to Zenodo and associated with the desposition_id

        Returns
        -------
        dict
            Returns the response retrieved via the Zenodo API
        """

        r = requests.put(
            f"{ZENODO_API_URL}/{deposition_id}",
            params=self.params,
            data=json.dumps(data),
            headers=ZENODO_HEADERS,
        )
        if not r.status_code == 200:
            raise Exception(
                f"{self.model_id}: Error ({r.status_code}!=200) during Zenodo upload (step 3: updating metadata): {r.json()}"
            )
        return r

    def publish(self, deposition_id: str) -> dict:
        """ Publish a zenodo upload.

        This makes the upload official, as it will then be publicly accessible and persistently stored on Zenodo with associated DOI.

        Parameters
        ----------
        deposition_id: str
            The deposition id assigned by Zenodo to the uploaded model file

        Returns
        -------
        dict
            Returns the response retrieved via the Zenodo API
        """

        # Get explicit user approval to publish on Zenodo. Published files cannot be deleted.
        is_user_sure = str(
            input(
                f"You are about to publish your model ({self.model_id}) on Zenodo ({ZENODO_API_URL}/{deposition_id}/actions/publish). If you are sure you would like to proceed, type 'Yes': "
            )
        )
        if is_user_sure == "Yes":
            r = requests.post(
                f"{ZENODO_API_URL}/{deposition_id}/actions/publish",
                params=self.params,
            )
        else:
            raise Exception(
                f"{self.model_id}: Error during Zenodo upload (step 4: publishing uploaded model) due to user opt-out: You typed '{is_user_sure}' instead of 'Yes'. Model was not published. Try again. Your Zenodo deposition ID (if retrieved): '{deposition_id}'."
            )
        if not r.status_code == 202:
            raise Exception(
                f"{self.model_id}: Error ({r.status_code}!=202) during Zenodo upload (step 4: publishing uploaded model): {r.json()}"
            )
        logging.info(
            f"{self.model_id}: Congratulations! Your model was successfully pushed to Zenodo with DOI '{r.json()['doi']}'. "
            f"Find it here: '{r.json()['links']['record_html']}"
        )
        logging.debug(
            f"{self.model_id}: Full Zenodo API response after successful publishing of model: {r.json()}"
        )
        return r

    def push(
        self,
        metadata: dict,
        package_path: str,
        package_name: str,
        creator_name: str,
        creator_affiliation: str,
        model_description: str = "",
    ):
        """ Upload the model files as zip archive to a public Zenodo repository where the model will be persistently stored.

        Get your Zenodo access token here: https://zenodo.org/account/settings/applications/tokens/new/ (Enable scopes `deposit:actions` and `deposit:write`)

        Parameters
        ----------
        metadata: dict
            The model's corresponding metadata
        package_path: dict
            The path to the packaged model files
        package_name: dict
            The name of the packaged model files
        creator_name: str
            the creator name that will appear on the corresponding Zenodo model upload homepage
        creator_affiliation: str
            the creator affiliation that will appear on the corresponding Zenodo model upload homepage
        model_description: list
            the model_description that will appear on the corresponding Zenodo model upload homepage

        Returns
        -------
        str
            Returns the url pointing to the corresponding Zenodo model upload homepage
        """

        # Check if zip ffile exists, else create new one for upload.
        filename, file_path = self.locate_or_create_model_zip_file(
            package_path=package_path, package_name=package_name
        )

        # create empty upload to Zenodo to get deposition_id and bucket_url
        response = self.empty_upload()
        logging.debug(f"API Response after creating empty upload template: {response}")

        # Get the deposition id from the response
        deposition_id = response.json()["id"]

        # Using bucket as defined by Zenodo API for zip file model upload
        bucket_url = response.json()["links"]["bucket"]

        response = self.upload(
            file_path=file_path,
            filename=filename,
            bucket_url=bucket_url,
        )
        logging.debug(
            f"API Response after uploading model to '{bucket_url}': {response}"
        )

        # get the model description i.e. model type, metadata info, etc.
        description = self.create_upload_description(
            metadata=metadata, model_description=model_description
        )

        # get the data that includes description, but also creator information
        data = self.create_upload_json_data(
            description=description,
            creator_name=creator_name,
            creator_affiliation=creator_affiliation,
        )

        # upload the model zip file and its descriptive data
        response = self.upload_descriptive_data(deposition_id=deposition_id, data=data)
        logging.debug(
            f"API Response after uploading descriptive model data: {response}"
        )

        # publish to Zenodo. Model will get DOI after this step and become part of Zenodo's permanent record.
        response = self.publish(deposition_id=deposition_id)
        logging.debug(
            f"API Response after publishing the deposition {deposition_id} on Zenodo: {response}"
        )
        return response.json()["links"]["record_html"]  # zenodo_record_url

    def __repr__(self):
        return f"ZenodoModelUploader(model_id={self.model_id}, zenodo_url={ZENODO_API_URL})"

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
