# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""Model contributor class that tests models, creates metadata entries, uploads and contributes them to medigan.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""

from __future__ import absolute_import

import importlib
import logging
import sys
from pathlib import Path

from ..constants import (
    CONFIG_FILE_KEY_DEPENDENCIES,
    CONFIG_FILE_KEY_EXECUTION,
    CONFIG_FILE_KEY_GENERATE,
    CONFIG_FILE_KEY_GENERATE_NAME,
    CONFIG_FILE_KEY_MODEL_EXTENSION,
    CONFIG_FILE_KEY_MODEL_NAME,
    CONFIG_FILE_KEY_PACKAGE_LINK,
    CONFIG_FILE_KEY_PACKAGE_NAME,
    CONFIG_TEMPLATE_FILE_NAME_AND_EXTENSION,
    INIT_PY_FILE,
    TEMPLATE_FOLDER,
)
from ..utils import Utils
from .zenodo_model_uploader import ZenodoModelUploader


class ModelContributor:
    """`ModelContributor` class: Contributes a user's local model to the public medigan library

    TODO
    """

    def __init__(
        self,
        model_id: str,
        init_py_path: str,
    ):
        self.validate_model_id(model_id)
        self.model_id = model_id
        self.init_py_path = init_py_path
        self.validate_init_py_path(init_py_path)
        self.package_path = self.init_py_path.replace(INIT_PY_FILE, "")
        self.package_name = Path(self.package_path).name
        self.metadata_file_path = ""  # Default is relative path to package root.
        self.validate_local_model_import()
        self.zenodo_model_uploader = None
        self.github_model_uploader = None

    ############################ VALIDATION ############################

    def validate_model_id(
        self, model_id: str, max_chars: int = 30, min_chars: int = 13
    ) -> bool:
        """TODO"""

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
        """TODO"""

        assert (
            Path(init_py_path).exists() and Path(init_py_path).is_file()
        ), f"{self.model_id}: The path to your model's __init__.py function does not exist or does not point to a file. Please revise path {init_py_path}. Note: You can find an __init__.py example in /templates in https://github.com/RichardObi/medigan"
        assert Utils.is_file_in(
            folder_path=self.init_py_path.replace(f"/{INIT_PY_FILE}", ""),
            filename=INIT_PY_FILE,
        ), f"{self.model_id}: No __init__.py was found in your path {init_py_path}. Please revise. Note: You can find an __init__.py example in /templates in https://github.com/RichardObi/medigan"

    def validate_and_update_model_weights_path(self) -> str:
        """Check if the model files can be found in the `package_path` or based on the `path_to_metadata`.

        Ideally, the user provided `package_path` and the `path_to_metadata` should both point to the same model package
        containing weights, config, license, etc. Here we check both of these paths to find the model weights.

        TODO Further docstring
        """

        metadata_dir_path = Path(self.metadata_file_path).parent

        potential_weight_paths: list = []

        execution_metadata = self.metadata[self.model_id][CONFIG_FILE_KEY_EXECUTION]

        # package_path + package_path + file + extension
        try:
            potential_weight_paths.append(
                Path(
                    self.package_path
                    + f"/{execution_metadata[CONFIG_FILE_KEY_MODEL_NAME]}{execution_metadata[CONFIG_FILE_KEY_MODEL_EXTENSION]}"
                )
            )
        except KeyError as e:
            raise e

        # metadata_dir + package_path + file + extension
        try:
            potential_weight_paths.append(
                Path(
                    str(metadata_dir_path)
                    + f"/{execution_metadata[CONFIG_FILE_KEY_MODEL_NAME]}{execution_metadata[CONFIG_FILE_KEY_MODEL_EXTENSION]}"
                )
            )
        except KeyError as e:
            raise e

        # metadata_dir + package_path + file + extension
        try:
            potential_weight_paths.append(
                Path(
                    str(metadata_dir_path)
                    + "/"
                    + self.package_path
                    + f"/{execution_metadata[CONFIG_FILE_KEY_MODEL_NAME]}{execution_metadata[CONFIG_FILE_KEY_MODEL_EXTENSION]}"
                )
            )
        except KeyError as e:
            raise e

        for potential_weight_path in potential_weight_paths:
            if potential_weight_path.is_file():
                # Checking if there is a weights/checkpoint (model name + extension) file in the package /metadata path
                self.package_path = str(
                    Path(potential_weight_path).parent.resolve(strict=False)
                )  # strict=False, as models might be not on user's disc.
                self.metadata[self.model_id][CONFIG_FILE_KEY_EXECUTION][
                    CONFIG_FILE_KEY_PACKAGE_LINK
                ] = self.package_path
                return self.metadata
        raise FileNotFoundError(
            f"{self.model_id}: Error validating metadata. There was no valid model weights file found. Please revise. Tested paths: '{potential_weight_paths}'"
        )

    def validate_local_model_import(self):
        """TODO"""

        # Validation: Import module as python library to check if generate function is inside the
        # path_to_script_w_generate_function python file and no errors occur.
        try:
            sys.path.insert(1, str(self.package_path).replace(self.package_name, ""))
            importlib.import_module(name=self.package_name)
        except Exception as e:
            raise Exception(
                f"{self.model_id}: Error while testing importlib model import. Is your {INIT_PY_FILE} erroneous? Please revise if the provided path ({self.init_py_path}) is valid and accessible and try again."
            ) from e

    ############################ UPLOAD ############################

    def push_to_zenodo(
        self,
        access_token: str,
        creator_name: str,
        creator_affiliation: str,
        model_description: str = "",
    ):
        """TODO

        Get zenodo access token from https://zenodo.org/account/settings/applications/tokens/new/
        """
        if self.zenodo_model_uploader is None:
            self.zenodo_model_uploader = ZenodoModelUploader(
                model_id=self.model_id, access_token=access_token
            )
        self.zenodo_model_uploader.push(
            metadata=self.metadata,
            package_path=self.package_path,
            package_name=self.package_name,
            creator_name=creator_name,
            creator_affiliation=creator_affiliation,
            model_description=model_description,
        )

    ############################ METADATA ############################

    def load_metadata_template(self):
        """TODO"""

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
        """TODO"""

        if Path(metadata_file_path).is_file():
            self.metadata = Utils.read_in_json(path_as_string=metadata_file_path)
            self.metadata_file_path = metadata_file_path
        elif Path(metadata_file_path + "/metadata.json").is_file():
            self.metadata = Utils.read_in_json(
                path_as_string=metadata_file_path + "/metadata.json"
            )
            self.metadata_file_path = metadata_file_path + "/metadata.json"
        else:
            raise FileNotFoundError(
                f"{self.model_id}: No metadata json file was found in the path you provided ({metadata_file_path}). "
                f"If you do not have a metadata file, create one using the add_metadata_from_input() function."
            )
        self.validate_and_update_model_weights_path()
        return self.metadata

    def add_metadata_from_input(
        self,
        model_weights_name: str = None,
        model_weights_extension: str = None,
        generate_method_name: str = None,
        dependencies: list = [],
        fill_more_fields_interactively: bool = True,
        output_path: str = "config",
    ):
        """TODO"""

        # Get the metadata template to guide data structure and formatting of metadata.
        self.metadata_template = self.load_metadata_template()

        # Generate metadata with variables provided as parameters
        metadata = self.metadata_template[self.model_id][CONFIG_FILE_KEY_EXECUTION]
        metadata.update({CONFIG_FILE_KEY_PACKAGE_LINK: self.package_path})
        metadata.update({CONFIG_FILE_KEY_PACKAGE_NAME: self.package_name})
        metadata.update({CONFIG_FILE_KEY_MODEL_NAME: model_weights_name})
        metadata.update({CONFIG_FILE_KEY_MODEL_EXTENSION: model_weights_extension})
        metadata.update({CONFIG_FILE_KEY_DEPENDENCIES: dependencies})
        metadata[CONFIG_FILE_KEY_GENERATE][
            CONFIG_FILE_KEY_GENERATE_NAME
        ] = generate_method_name
        metadata_final = self.metadata_template
        metadata_final[self.model_id].update({CONFIG_FILE_KEY_EXECUTION: metadata})

        Utils.store_dict_as(
            dictionary=metadata_final,
            extension=".json",
            output_path=output_path,
            filename=self.model_id,
        )
        logging.info(
            f"{self.model_id}: Your model's metadata was stored in {output_path}."
        )

        if fill_more_fields_interactively:
            # Add more information to the metadata dict via user prompts
            metadata_final = self._recursively_fill_metadata(metadata=metadata_final)
            # Store again as additional fields should have now been filled
            Utils.store_dict_as(
                dictionary=metadata_final,
                extension=".json",
                output_path=output_path,
                filename=self.model_id,
            )
            logging.info(
                f"{self.model_id}: Your model's metadata was updated. Find it in {output_path}/{self.model_id}.json"
            )

        self.metadata = metadata_final
        self.validate_and_update_model_weights_path()

        return self.metadata

    def is_key_value_set_or_dict(self, key: str, metadata: dict, nested_key) -> bool:
        """TODO"""

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
        """TODO"""

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
                    value_assigned = (
                        [value.strip() for value in input_value.split(",")]
                        if input_value != ""
                        else []
                    )
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
        return f"ModelContributor(model_id={self.model_id}, metadata={self.metadata})"

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
