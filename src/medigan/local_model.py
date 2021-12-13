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

# Import library internal modules
from .config_manager import ConfigManager
from .constants import CONFIG_FILE_FOLDER


class LocalModel:
    """ `LocalModel` class: A user's local model that can be run, tested and integrated into medigan. """

    def __init__(
            self,
            model_id: str,
            metadata: dict,
            metadata_path: str = None,
            root_folder_path: str = None,
            generate_method_script_path: str = None,
            generate_method_name: str = None,
    ):

        if self.validate_model_id(model_id): self.model_id = model_id

        if metadata_path is None:
            self.metadata_path = f"{CONFIG_FILE_FOLDER}/{model_id}
        else:
            self.validate_metadata(metadata=None, metadata_path=metadata_path)

        if metadata is not None and self.validate_metadata(metadata=metadata,
                                                           metadata_path=None): self.metadata = metadata


    def run(self):
        # TODO: Init a model_executor if not yet initialized
        # TODO: return generate method of model_executor
        # What metadata is really needed for running the model? -> Retrieve via run() function arguments.
        pass

    def validate_model_id(self, model_id: str = None) -> bool:
        # TODO: Assert model ID not None and length of characters and if it starts with 5 numbers. Raise exception logging an example of a good model_id to user
        return True

    def validate_metadata(self, metadata: dict = None, metadata_path: str = None) -> bool:
        if metadata is not None:
            # TODO: Assert metadata not None and the existence of the most important entries of the metadata.
            pass
        elif metadata_path is not None:
            metadata_file = Path(self.metadata_path)
            if not metadata_file.is_file():
                return False
            # TODO: Assert metadata not None and the existence of the most important entries of the metadata.
        return True

    def create_model_metadata(self, is_stored: bool = False, output_path: str = "/config"):
        # TODO check if there is already a metadata file named by model_id where it should be (e.g. inside folder /config)
        if self.validate_metadata(metadata_path=self.metadata_path):
            # TODO Warn user that valid metadata is already here. Should be deleted manually first if user wants to generate a new one.
            pass
        self.config_manager = ConfigManager(use_config_template=True)

        # TODO insert the known mandatory metadata into metadata template

        # TODO insert the optional metadata from metadata template recursively via user prompts.
        self.metadata = self._recursively_fill_metadata(metadata_template=self.config_manager.config_dict)

        # TODO: The whole metadata dict should be nested below the model_id, before storing

        # TODO store and write to disk
        if is_stored:
            self.store_metadata(output_path=output_path)

    def is_key_value_set(self, key: str, metadata: dict, nested_key) -> bool:
        if metadata.get(key) is not None and metadata.get(key) != "" and not metadata.get(key):
            # Note: If metadata.get(key) is not referencing a list nor dict and is of type(bool) and False, user has to repeat entry here.
            logging.debug(
                f"{self.model_id}: Key value pair ({key}:{metadata.get(key)}) already exists in metadata for key "
                f"'{nested_key}'. Not prompting user to insert value for this key.")
            return True
        return False

    def _recursively_fill_metadata(self, metadata_template: dict, nested_key: str = '') -> dict:
        # Prompt user for optional metadata input
        metadata: dict = {}
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

    def store_metadata(self, filetype='json', output_path="/config"):
        # TODO assert filetype != "json": Not yet implemented exception
        # TODO parse as json and store by model_id.json
        pass

    def create_model_init_function(self):
        # TODO: Check if there is a __init__.py file there. Except if generate_script_path is None.
        # TODO: Else: Import generate_method_name from generate script in generated __init__.py.
        pass

    def __str__(self):
        return json.dumps(
            {'model_id': self.model_id, 'metadata': self.metadata, 'root_folder_path': self.root_folder_path})

    def __repr__(self):
        return f'ModelMatchCandidate(model_id={self.model_id}, metadata={self.metadata}, root_folder_path: {self.root_folder_path})'

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
