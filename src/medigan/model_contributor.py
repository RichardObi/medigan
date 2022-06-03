# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""Model contributor class that tests models, creates metadata entries, uploads and contributes them to medigan.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""

from __future__ import absolute_import

import importlib
import json
import logging
import shutil
import sys
from pathlib import Path

import requests

from .config_manager import ConfigManager
from .constants import (
    CONFIG_FILE_KEY_DEPENDENCIES,
    CONFIG_FILE_KEY_DESCRIPTION,
    CONFIG_FILE_KEY_EXECUTION,
    CONFIG_FILE_KEY_GENERATE,
    CONFIG_FILE_KEY_GENERATE_ARGS,
    CONFIG_FILE_KEY_GENERATE_ARGS_BASE,
    CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE,
    CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES,
    CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH,
    CONFIG_FILE_KEY_GENERATE_ARGS_SAVE_IMAGES,
    CONFIG_FILE_KEY_GENERATE_NAME,
    CONFIG_FILE_KEY_IMAGE_SIZE,
    CONFIG_FILE_KEY_MODEL_EXTENSION,
    CONFIG_FILE_KEY_MODEL_NAME,
    CONFIG_FILE_KEY_PACKAGE_LINK,
    CONFIG_FILE_KEY_PACKAGE_NAME,
    CONFIG_FILE_KEY_SELECTION,
    CONFIG_FILE_KEY_TAGS,
    CONFIG_TEMPLATE_FILE_NAME_AND_EXTENSION,
    INIT_PY_FILE,
    TEMPLATE_FOLDER,
    ZENODO_GENERIC_MODEL_DESCRIPTION,
)
from .utils import Utils


class ModelContributor:
    """`ModelContributor` class: Contributes a user's local model to the public medigan library"""

    def __init__(
        self,
        model_id: str,
        init_py_path: str,
    ):
        self.validate_model_id(model_id)
        self.model_id = model_id
        self.validate_init_py_path(init_py_path)
        self.init_py_path = init_py_path
        self.package_path = self.init_py_path.replace(INIT_PY_FILE, "")
        self.package_name = Path(self.package_path).name
        self.validate_local_model_import()

    ############################ VALIDATION ############################

    def validate_model_id(
        self, model_id: str, max_chars: int = 30, min_chars: int = 13
    ) -> bool:
        num_chars = len(model_id)
        assert (
            num_chars <= max_chars
        ), f"The model_id {model_id} is too large ({num_chars}). Please reduce to a maximum of {max_chars} characters. Format Convention: '00001_GANTYPE_MODALITY'"
        assert (
            num_chars >= min_chars
        ), f"The model_id {model_id} is too small ({num_chars}). Please reduce to a minimum of {min_chars} characters. Format Convention: '00001_GANTYPE_MODALITY'"
        for i in range(5):
            assert model_id[
                i
            ].isdigit(), f"Your model_id's ({model_id}) character '{model_id[i]}' at position {i} is not a digit. The first 5 characters should be digits as in '00001_GANTYPE_MODALITY'. Please adjust."
        return True

    def validate_init_py_path(self, init_py_path):
        assert (
            Path(init_py_path).exists() and Path(init_py_path).is_file()
        ), f"{self.model_id}: The path to your model's __init__.py function does not exist or does not point to a file. Please revise path {init_py_path}."
        assert Utils.is_file_in(
            folder_path=self.init_py_path.replace(INIT_PY_FILE, ""),
            filename=INIT_PY_FILE,
        ), f"{self.model_id}: No __init__.py was found in your path {init_py_path}. Please revise."

    def validate_local_model_import(self):
        # Validation: Import module as python library to check if generate function is inside the
        # path_to_script_w_generate_function python file and no errors occur.
        try:
            sys.path.insert(1, str(self.package_path).replace(self.package_name, ""))
            importlib.import_module(name=self.package_name)
        except Exception as e:
            raise Exception(
                f"{self.model_id}: Error while testing importlib model import. Is your {INIT_PY_FILE} erroneous? Please alos revise if the provided path ({self.init_py_path}) is valid and accessible and try again."
            ) from e

    ############################ UPLOAD ############################

    def push_to_zenodo(
        self,
        access_token: str,
        creator_name: str,
        creator_affiliation: str,
        model_description: str = "",
        deposition_id: str = None,
    ):
        # Get access token from https://zenodo.org/account/settings/applications/tokens/new/
        zenodo_model_data = ""
        if deposition_id is not None:
            # Create a zip archive for the model
            root_dir = Path(self.package_path).parent
            file_name = self.package_name
            shutil.make_archive(
                base_name=self.package_name,
                extension="zip",
                base_dir=self.package_path,
                root_dir=root_dir,
            )

            ####### Using Zenodo API for creating empty zenodo upload

            headers = {"Content-Type": "application/json"}
            params = {"access_token": access_token}
            r = requests.post(
                "https://sandbox.zenodo.org/api/deposit/depositions",
                params=params,
                json={},
                headers=headers,
            )
            if not r.status_code == 201:
                raise Exception(
                    f"{self.model_id}: Error ({r.status_code}!=201) during Zenodo upload (step 1: creating empty upload template): {r.json()}"
                )

            ####### Using Zenodo API for zip file model upload

            bucket_url = r.json()["links"]["bucket"]
            file_path = root_dir + "/" + file_name

            # The target URL is a combination of the bucket link with the desired filename seperated by a slash.
            with open(file_path, "rb") as fp:
                r = requests.put(
                    "%s/%s" % (bucket_url, file_name),
                    data=fp,
                    params=params,
                )

            if not r.status_code == 200:
                raise Exception(
                    f"{self.model_id}: Error ({r.status_code}!=200) during Zenodo upload (step 2: uploading model as zip file): {r.json()}"
                )

            # Get the deposition id from the response
            deposition_id = r.json()["id"]

            ####### Using Zenodo API to update metadata of zip file upload
            try:
                tags = f"\n Tags: {self.metadata[self.model_id][CONFIG_FILE_KEY_SELECTION][CONFIG_FILE_KEY_TAGS]}"
            except:
                tags = ""
            try:
                description_from_config = f"\n Description from model config: {json.dumps(self.metadata[self.model_id][CONFIG_FILE_KEY_DESCRIPTION])}"
            except:
                description_from_config = ""

            description = f"{model_description} \n Model: {self.model_id}. \n Upload via: API {tags} {ZENODO_GENERIC_MODEL_DESCRIPTION} {description_from_config}"

            data = {
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

            r = requests.put(
                "https://zenodo.org/api/deposit/depositions/%s" % deposition_id,
                params={"access_token": access_token},
                data=json.dumps(data),
                headers=headers,
            )
            if not r.status_code == 200:
                raise Exception(
                    f"{self.model_id}: Error ({r.status_code}!=200) during Zenodo upload (step 3: updating metadata): {r.json()}"
                )

            zenodo_model_data = f"\n Model data: {r.json()}"

        ####### Using Zenodo API to publish uploaded model

        # Get explicit user approval to publish on Zenodo. Published files cannot be deleted.
        is_user_sure = str(
            input(
                f"You are about to publish your model ({self.model_id}) on Zenodo. {zenodo_model_data} \n If you are sure you wold like to proceed, type 'Yes': "
            )
        )
        if is_user_sure == "Yes":
            r = requests.post(
                f"https://zenodo.org/api/deposit/depositions/{deposition_id}/actions/publish",
                params={"access_token": access_token},
            )
        else:
            raise Exception(
                f"{self.model_id}: Error during Zenodo upload (step 4: publishing uploaded model) due to user opt-out: You typed '{is_user_sure}' instead of 'Yes'. Model was not published. Try again providing Zenodo ID: '{deposition_id}'."
            )
        if not r.status_code == 202:
            raise Exception(
                f"{self.model_id}: Error ({r.status_code}!=202) during Zenodo upload (step 4: publishing uploaded model): {r.json()}"
            )

    def push_to_repo(self):
        # Get access_token from https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

        # TODO Import libraries Gitpython and PyGithub
        # Info: https://stackoverflow.com/a/61533333

        # TODO git clone (Gitpython)
        #  Fork/Clone medigan repo into local folder

        # TODO git add (Gitpython)
        #  add the global.json to the medigan repo

        # TODO git commit (Gitpython)
        #  add the global.json to the medigan repo

        # TODO git push (Gitpython)
        # create upstream branch on Github and push code there

        # TODO github PR (PyGithub)
        # create a Github pull request (PR) from forked repo to the original medigan repo (https://github.com/RichardObi/medigan)

        # TODO github assign_reviewer (PyGithub)
        # assign user 'RichardObi' as reviewer using https://pygithub.readthedocs.io/en/latest/github_objects/PullRequest.html#github.PullRequest.PullRequest.create_review_request

        raise NotImplementedError

    ############################ METADATA ############################

    def load_metadata_template(self):
        path_to_metadata_template = Path(
            f"{TEMPLATE_FOLDER}/{CONFIG_TEMPLATE_FILE_NAME_AND_EXTENSION}"
        )
        metadata_template = Utils.read_in_json(path_as_string=path_to_metadata_template)
        if self.model_id is not None:
            # Replacing the placeholder id of template with model_id
            metadata_template[self.model_id] = metadata_template[
                list(metadata_template)[0]
            ]
            del metadata_template[list(metadata_template)[0]]
        return metadata_template

    def add_metadata_from_file(self, metadata_file_path):
        if Path(metadata_file_path).is_file():
            self.metadata = Utils.read_in_json(path_as_string=metadata_file_path)
            return self.metadata
        else:
            raise FileNotFoundError(
                f"{self.model_id}: No metadata json file was found in the path you provided ({metadata_file_path}). "
                f"If you do not have a metadata file, create one using the add_metadata_from_input() function."
            )

    def add_metadata_from_input(
        self,
        model_weights_name: str = None,
        model_weights_extension: str = None,
        generate_method_name: str = None,
        image_size: list = [],
        dependencies: list = [],
        fill_more_fields_interactively: bool = True,
        output_path: str = "/config",
    ):
        # Get the metadata template to guide data structure and formatting of metadata.
        self.metadata_template = self.load_metadata_template(model_id=self.model_id)

        # Generate metadata with variables provided as parameters
        metadata = self.metadata_template[self.model_id][CONFIG_FILE_KEY_EXECUTION]
        metadata.update({CONFIG_FILE_KEY_PACKAGE_LINK: self.package_path})
        metadata.update({CONFIG_FILE_KEY_PACKAGE_NAME: self.package_name})
        metadata.update({CONFIG_FILE_KEY_MODEL_NAME: model_weights_name})
        metadata.update({CONFIG_FILE_KEY_MODEL_EXTENSION: model_weights_extension})
        metadata.update({CONFIG_FILE_KEY_DEPENDENCIES: dependencies})
        metadata.update({CONFIG_FILE_KEY_IMAGE_SIZE: image_size})
        metadata[CONFIG_FILE_KEY_GENERATE][
            CONFIG_FILE_KEY_GENERATE_NAME
        ] = generate_method_name
        metadata_final = self.metadata_template
        metadata_final[self.model_id].update({CONFIG_FILE_KEY_EXECUTION: metadata})
        logging.debug(
            f"The following metadata was automatically created based on your input: {metadata_final}"
        )
        self.store_metadata(output_path, metadata=metadata_final)
        if fill_more_fields_interactively:
            metadata_final = self._recursively_fill_metadata(metadata=metadata_final)
        self.store_metadata(output_path=output_path, metadata=metadata_final)
        self.metadata = metadata_final
        return self.metadata

    def store_metadata(self, output_path: str = "config/", metadata: dict = None):
        logging.debug(f"{self.model_id}: Metadata before storing: {metadata}")
        Utils.store_dict_as(
            dictionary=metadata, extension=".json", output_path=output_path
        )
        logging.info(
            f"{self.model_id}: Your model's metadata was stored in {output_path}."
        )

    def is_key_value_set_or_dict(self, key: str, metadata: dict, nested_key) -> bool:
        if (
            metadata.get(key) is None
            or metadata.get(key) == ""
            or (isinstance(metadata.get(key), list) and not metadata.get(key))
            or isinstance(metadata.get(key), dict)
        ):
            # Note: If metadata.get(key) is referencing a dict, we always want to go inside the dict and add values.
            return False
        else:
            logging.debug(
                f"{self.model_id}: Key value pair ({key}:{metadata.get(key)}) already exists in metadata for key "
                f"'{nested_key}'. Not prompting user to insert value for this key."
            )
            return True

    def _recursively_fill_metadata(
        self, metadata_template: dict = None, metadata: dict = {}, nested_key: str = ""
    ) -> dict:
        if metadata_template is None:
            metadata_template = self.metadata_template
        # Prompt user for optional metadata input
        retrieved_nested_key = nested_key
        for key in metadata_template:
            # nested_key to know where we are inside the metadata dict.
            nested_key = (
                key if retrieved_nested_key == "" else f"{retrieved_nested_key}.{key}"
            )
            if not self.is_key_value_set_or_dict(
                key=key, metadata=metadata, nested_key=nested_key
            ):
                value_template = metadata_template.get(key)
                if value_template is None:
                    input_value = input(
                        f"{self.model_id}: Please enter value of type float or int for your model for key '{nested_key}': "
                    )
                    try:
                        value_assigned = float(input_value.replace(",", "."))
                    except ValueError:
                        value_assigned = (
                            int(input_value) if input_value.isdigit() else None
                        )
                elif isinstance(value_template, list):
                    input_value = input(
                        f"{self.model_id}: Please enter a comma-separated list of values for your model for key: '{nested_key}': "
                    )
                    value_assigned = list(input_value) if input_value != "" else []
                elif isinstance(value_template, str):
                    value_assigned = str(
                        input(
                            f"{self.model_id}: Please enter value of type string for your model for key '{nested_key}': "
                        )
                    )
                elif isinstance(value_template, dict):
                    if len(value_template) == 0:
                        # If dict is empty, no recursion. Instead, we ask the user directly for input.
                        iterations = int(
                            input(
                                f"{self.model_id}: How many key-value pairs do you want to nest below key '{nested_key}' "
                                f"in your model's metadata. Type a number: "
                            )
                            or "0"
                        )
                        nested_metadata: dict = {}
                        for i in range(iterations):
                            nested_key_input = str(
                                input(f"{self.model_id}: Enter key {i + 1}: ")
                            )
                            nested_value_input = input(
                                f"{self.model_id}: For key{i + 1}={nested_key_input}, enter value: "
                            )
                            nested_metadata.update(
                                {nested_key_input: nested_value_input}
                            )
                        value_assigned = nested_metadata
                    else:
                        # From metadata, get the nested dict below the key. If metadata has no nested dict, get the
                        # template's nested dict instead, which is stored in value_template
                        temp_metadata = (
                            metadata.get(key)
                            if metadata.get(key) is not None
                            else value_template
                        )
                        # Filling nested dicts via recursion. value_assigned is of type dict in this case.
                        value_assigned = self._recursively_fill_metadata(
                            metadata_template=value_template,
                            nested_key=nested_key,
                            metadata=temp_metadata,
                        )
                logging.debug(
                    f"{self.model_id}: You provided this key-value pair: {key}={value_assigned}"
                )
                metadata.update({key: value_assigned})
        return metadata

    def __repr__(self):
        return f"ModelContributor(model_id={self.model_id})"

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
