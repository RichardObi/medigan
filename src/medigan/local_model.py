# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""LocalModel class that holds the information about a user's local, not yet contributed, generative model in medigan.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""

# Import python native libs
from __future__ import absolute_import

import json
import logging
from pathlib import Path

from .constants import CONFIG_FILE_FOLDER, CONFIG_TEMPLATE_FILE_NAME_AND_EXTENSION, CONFIG_FILE_KEY_EXECUTION, \
    CONFIG_FILE_KEY_GENERATE_NAME, CONFIG_FILE_KEY_PACKAGE_LINK, CONFIG_FILE_KEY_MODEL_EXTENSION, \
    CONFIG_FILE_KEY_PACKAGE_NAME, CONFIG_FILE_KEY_GENERATE, CONFIG_FILE_KEY_SELECTION, CONFIG_FILE_KEY_DEPENDENCIES, \
    CONFIG_FILE_KEY_GENERATE_ARGS, CONFIG_FILE_KEY_GENERATE_ARGS_BASE, CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE, \
    CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES, CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH, \
    CONFIG_FILE_KEY_GENERATE_ARGS_SAVE_IMAGES, CONFIG_FILE_KEY_IMAGE_SIZE, CONFIG_FILE_KEY_MODEL_NAME
# Import library internal modules
from .utils import Utils


class LocalModel:
    """ `LocalModel` class: A user's local model that can be run, tested and integrated into medigan. """

    def __init__(
            self,
            model_id: str = None,
            package_link: str = None,
            package_name: str = None,
            model_name: str = None,
            model_extension: str = None,
            generate_function_name: str = None,
            metadata_path: str = None,
            generate_method_script_path: str = None,
            are_optional_config_fields_requested: str = None,
            output_path: str = "/config",
            image_size: list = [],
            dependencies: list = [],
    ):
        if self.validate_model_id(model_id): self.model_id = model_id

        # TODO: Check if there is already a metadata file named by model_id where it should be (e.g. inside folder /config)
        # TODO Warn user that valid metadata is already here. Should be deleted manually first if user wants to generate a new one.

        if metadata_path is not None:
            if Path(metadata_path).is_file():
                metadata = Utils.read_in_json(path_as_string=metadata_path)[0]
            else:
                raise FileNotFoundError(
                    f"{self.model_id}: No metadata json file was found in thee path you provided ({metadata_path}). Please review.")
        else:
            # Generate metadata with variables provided as parameters of the LocalModel class.
            metadata = self.create_metadata(model_id=model_id, package_link=package_link,
                                            model_extension=model_extension,
                                            model_name=model_name, generate_function_name=generate_function_name,
                                            image_size=image_size, dependencies=dependencies, package_name=package_name)

        self.validate_metadata(metadata)

        if are_optional_config_fields_requested:
            metadata = self._recursively_fill_metadata(metadata_template=self.get_metadata_template(),
                                                       metadata=metadata)

        # Note: In case user added via prompt, we store the user's input before re-validating the final metadata.
        self.store_metadata(output_path=output_path)
        logging.info(f"{self.model_id}: Local model's metadata is stored in: {output_path}")

        if self.validate_metadata(metadata): self.metadata = metadata
        logging.info(f"{self.model_id}: Created local model's final validated metadata: {self.metadata}")

    def validate_model_id(self, model_id: str = None, max_chars: int = 30, min_chars: int = 13) -> bool:
        num_chars = str.count(model_id)
        assert num_chars > max_chars, f"The model_id {model_id} is too large ({num_chars}). Please reduce to a maximum of {max_chars} characters. Format Convention: '00001_GANTYPE_MODALITY'"
        assert num_chars < min_chars, f"The model_id {model_id} is too small ({num_chars}). Please reduce to a minimum of {min_chars} characters. Format Convention: '00001_GANTYPE_MODALITY'"
        for i in range(5):
            assert not model_id[
                i].is_digit(), f"Your model_id's ({model_id}) character '{model_id[i]}' at position {i} is not a digit. The first 5 characters should be digits as in '00001_GANTYPE_MODALITY'. Please adjust."
        return True

    def validate_metadata(self, metadata: dict = None) -> bool:
        # TODO: Simplify asserts
        # Assert metadata not None and the existence of the most important entries of the metadata.
        assert metadata is not None, f" {self.model_id}: Error validating metadata. metadata is None (metadata={metadata})."
        assert CONFIG_FILE_KEY_EXECUTION in metadata, f" {self.model_id}: Error validating metadata. metadata did not contain '{CONFIG_FILE_KEY_EXECUTION}'. Metadata : {metadata}"
        assert CONFIG_FILE_KEY_SELECTION in metadata, f" {self.model_id}: Error validating metadata ({metadata}). metadata did not contain '{CONFIG_FILE_KEY_SELECTION}'. Metadata : {metadata}"
        assert CONFIG_FILE_KEY_PACKAGE_LINK in metadata[CONFIG_FILE_KEY_EXECUTION], f" {self.model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_PACKAGE_LINK}'. Metadata: {metadata[CONFIG_FILE_KEY_EXECUTION]}"
        assert CONFIG_FILE_KEY_MODEL_EXTENSION in metadata[CONFIG_FILE_KEY_EXECUTION], f" {self.model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_MODEL_EXTENSION}'. Metadata: {metadata[CONFIG_FILE_KEY_EXECUTION]}"
        assert CONFIG_FILE_KEY_PACKAGE_NAME in metadata[CONFIG_FILE_KEY_EXECUTION], f" {self.model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_PACKAGE_NAME}'. Metadata: {metadata[CONFIG_FILE_KEY_EXECUTION]}"
        assert CONFIG_FILE_KEY_MODEL_NAME in metadata[CONFIG_FILE_KEY_EXECUTION], f" {self.model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_MODEL_NAME}'. Metadata: {metadata[CONFIG_FILE_KEY_EXECUTION]}"
        assert CONFIG_FILE_KEY_DEPENDENCIES in metadata[CONFIG_FILE_KEY_EXECUTION], f" {self.model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_DEPENDENCIES}'. Metadata: {metadata[CONFIG_FILE_KEY_EXECUTION]}"
        assert CONFIG_FILE_KEY_GENERATE in metadata[CONFIG_FILE_KEY_EXECUTION], f" {self.model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_GENERATE}'. Metadata: {metadata[CONFIG_FILE_KEY_EXECUTION]}"
        assert CONFIG_FILE_KEY_GENERATE_ARGS in metadata[CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_GENERATE], f" {self.model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_GENERATE_ARGS}'. Metadata: {metadata[CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_GENERATE]}"
        assert CONFIG_FILE_KEY_GENERATE_ARGS_BASE in metadata[CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_GENERATE][CONFIG_FILE_KEY_GENERATE_ARGS], f" {self.model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_GENERATE_ARGS_BASE}'. Metadata: {metadata[CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_GENERATE][CONFIG_FILE_KEY_GENERATE_ARGS]}"
        assert CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE in metadata[CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_GENERATE][CONFIG_FILE_KEY_GENERATE_ARGS][CONFIG_FILE_KEY_GENERATE_ARGS_BASE], f" {self.model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE}'. Metadata: {metadata[CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_GENERATE][CONFIG_FILE_KEY_GENERATE_ARGS][CONFIG_FILE_KEY_GENERATE_ARGS_BASE]}"
        assert CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES in metadata[CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_GENERATE][CONFIG_FILE_KEY_GENERATE_ARGS][CONFIG_FILE_KEY_GENERATE_ARGS_BASE], f" {self.model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES}'. Metadata: {metadata[CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_GENERATE][CONFIG_FILE_KEY_GENERATE_ARGS][CONFIG_FILE_KEY_GENERATE_ARGS_BASE]}"
        assert CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH in metadata[CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_GENERATE][CONFIG_FILE_KEY_GENERATE_ARGS][CONFIG_FILE_KEY_GENERATE_ARGS_BASE], f" {self.model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH}'. Metadata: {metadata[CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_GENERATE][CONFIG_FILE_KEY_GENERATE_ARGS][CONFIG_FILE_KEY_GENERATE_ARGS_BASE]}"
        assert CONFIG_FILE_KEY_GENERATE_ARGS_SAVE_IMAGES in metadata[CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_GENERATE][CONFIG_FILE_KEY_GENERATE_ARGS][CONFIG_FILE_KEY_GENERATE_ARGS_BASE], f" {self.model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_GENERATE_ARGS_SAVE_IMAGES}'. Metadata: {metadata[CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_GENERATE][CONFIG_FILE_KEY_GENERATE_ARGS][CONFIG_FILE_KEY_GENERATE_ARGS_BASE]}"
        return True

    def create_metadata(self, package_link: str = None, package_name: str = None, model_name: str = None,
                        model_extension: str = None,
                        generate_function_name: str = None, dependencies: list = [], image_size: list = []):
        # Insert the mandatory metadata into metadata template
        metadata_template = self.get_metadata_template()
        metadata = metadata_template[CONFIG_FILE_KEY_EXECUTION]
        metadata.update(CONFIG_FILE_KEY_PACKAGE_LINK, package_link)
        metadata.update(CONFIG_FILE_KEY_PACKAGE_NAME, package_name)
        metadata.update(CONFIG_FILE_KEY_MODEL_NAME, model_name)
        metadata.update(CONFIG_FILE_KEY_MODEL_EXTENSION, model_extension)
        metadata.update(CONFIG_FILE_KEY_DEPENDENCIES, dependencies)
        metadata.update(CONFIG_FILE_KEY_IMAGE_SIZE, image_size)
        metadata[CONFIG_FILE_KEY_GENERATE][CONFIG_FILE_KEY_GENERATE_NAME] = generate_function_name
        metadata_template.update(CONFIG_FILE_KEY_EXECUTION, metadata)
        return metadata_template

    @staticmethod
    def get_metadata_template(path_to_metadata_template: str = None) -> dict:
        if path_to_metadata_template is None:
            path_to_metadata_template = Path(f"{CONFIG_FILE_FOLDER}/{CONFIG_TEMPLATE_FILE_NAME_AND_EXTENSION}")
        return Utils.read_in_json(path_as_string=path_to_metadata_template)

    def store_metadata(self, output_path: str = "/config"):
        # medigan data structurr convention: Nesting the whole metadata dict below the model_id before storing.
        metadata = {self.model_id: self.metadata}
        Utils.store_dict_as(dictionary=metadata, extension=".json", output_path=output_path,
                            filename=f"{self.model_id}.json")

    def is_key_value_set(self, key: str, metadata: dict, nested_key) -> bool:
        if metadata.get(key) is not None and metadata.get(key) != "" and not metadata.get(key):
            # Note: If metadata.get(key) is not referencing a list nor dict and is of type(bool) and False, user has to repeat entry here.
            logging.debug(
                f"{self.model_id}: Key value pair ({key}:{metadata.get(key)}) already exists in metadata for key "
                f"'{nested_key}'. Not prompting user to insert value for this key.")
            return True
        return False

    def _recursively_fill_metadata(self, metadata_template: dict, metadata: dict = {}, nested_key: str = '') -> dict:
        # Prompt user for optional metadata input
        for key in metadata_template:
            # nested_key to know where we are inside the metadata dict.
            nested_key = key if nested_key == '' else f"{nested_key}.{key}"
            if not self.is_key_value_set(key=key, metadata=metadata, nested_key=nested_key):
                value_template = metadata_template.get(key)
                if value_template is None:
                    value_assigned = input(
                        f"{self.model_id}: Please enter value for your model for key: '{nested_key}'")
                elif isinstance(value_template, list):
                    value_assigned = list(input(
                        f"{self.model_id}: Please enter a comma-separated list of values for your model for key: '{nested_key}'"))
                elif isinstance(value_template, str):
                    value_assigned = str(
                        input(
                            f"{self.model_id}: Please enter value of type string for your model for key: '{nested_key}'"))
                elif isinstance(value_template, float):
                    value_assigned = float(
                        input(
                            f"{self.model_id}: Please enter value of type float for your model for key: '{nested_key}'"))
                elif isinstance(value_template, int):
                    value_assigned = int(
                        input(
                            f"{self.model_id}: Please enter value of type int for your model for key: '{nested_key}'"))
                elif isinstance(value_template, dict):
                    if len(value_template) == 0:
                        # If dict is empty, no recursion. Instead, we ask the user directly for input.
                        iterations = int(input(
                            f"{self.model_id}: How many key-value pairs do you want to nest below key '{nested_key}' "
                            f"in your model's metadata. Type a number."))
                        nested_metadata: dict = {}
                        for i in range(iterations):
                            nested_key_input = str(input(f"{self.model_id}: Enter key{i}."))
                            nested_value_input = input(f"{self.model_id}: Enter value{i}.")
                            nested_metadata.update(nested_key_input, nested_value_input)
                        value_assigned = nested_metadata
                    else:
                        # Filling nested dicts via recursion. value_assigned is of type dict in this case.
                        value_assigned = self._recursively_fill_metadata(metadata_template=value_template,
                                                                         nested_key=nested_key)
                metadata.update(key, value_assigned)
        return metadata

    def create_model_init_function(self):
        # TODO: Check if there is a __init__.py file there. Except if generate_script_path is None.
        # TODO: Else: Import generate_method_name from generate script in generated __init__.py.
        raise NotImplementedError

    def __str__(self):
        return json.dumps(
            {'model_id': self.model_id, 'metadata': self.metadata, 'root_folder_path': self.root_folder_path})

    def __repr__(self):
        return f'ModelMatchCandidate(model_id={self.model_id}, metadata={self.metadata}, root_folder_path: {self.root_folder_path})'

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
