# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""LocalModel class that holds the information about a user's local, not yet contributed, generative model in medigan.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""

# Import python native libs
from __future__ import absolute_import

import importlib
import json
import logging
import sys
from pathlib import Path

from .constants import CONFIG_FILE_FOLDER, CONFIG_TEMPLATE_FILE_NAME_AND_EXTENSION, CONFIG_FILE_KEY_EXECUTION, \
    CONFIG_FILE_KEY_GENERATE_NAME, CONFIG_FILE_KEY_PACKAGE_LINK, CONFIG_FILE_KEY_MODEL_EXTENSION, \
    CONFIG_FILE_KEY_PACKAGE_NAME, CONFIG_FILE_KEY_GENERATE, CONFIG_FILE_KEY_SELECTION, CONFIG_FILE_KEY_DEPENDENCIES, \
    CONFIG_FILE_KEY_GENERATE_ARGS, CONFIG_FILE_KEY_GENERATE_ARGS_BASE, CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE, \
    CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES, CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH, \
    CONFIG_FILE_KEY_GENERATE_ARGS_SAVE_IMAGES, CONFIG_FILE_KEY_IMAGE_SIZE, CONFIG_FILE_KEY_MODEL_NAME, INIT_PY_FILE
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
            generate_method_name: str = None,
            metadata_path: str = None,
            path_to_script_w_generate_function: str = None,
            are_optional_config_fields_requested: bool = True,
            output_path: str = "config/",
            image_size: list = [],
            dependencies: list = [],
    ):
        self.metadata_template = None

        if metadata_path is not None:
            metadata = self.create_metadata_from_path(metadata_path=metadata_path)
            model_id = list(metadata)[0]
            # Check if the model_id is correctly formatted
            if self.validate_model_id(model_id): self.model_id = model_id
        else:
            # Check if the model_id is correctly formatted
            if self.validate_model_id(model_id): self.model_id = model_id
            logging.info(f"{self.model_id}: No metadata_path was provided to initialize your LocalModel. "
                         f"Now creating model using params ("
                         f"package_link={package_link}, "
                         f"package_name={package_name}, "
                         f"model_name={model_name},"
                         f"model_extension={model_extension}, "
                         f"generate_method_name={generate_method_name}, "
                         f"image_size={image_size}, "
                         f"dependencies={dependencies}.")
            # Get the metadata template to guide structuring and formating of metadata.
            self.metadata_template = self.load_metadata_template(model_id=self.model_id)

            # Generate metadata with variables provided as parameters of the LocalModel class.
            metadata = self.create_metadata(package_link=package_link,
                                            model_extension=model_extension,
                                            model_name=model_name, generate_method_name=generate_method_name,
                                            image_size=image_size, dependencies=dependencies, package_name=package_name)

        # Validate if the metadata is contains necessary fields as it should at this point.
        self.validate_metadata(metadata)

        # Ask the user via input prompts for additional optional metadata
        if are_optional_config_fields_requested:
            if self.metadata_template is None:
                self.metadata_template = self.load_metadata_template(model_id=self.model_id)
            metadata = self._recursively_fill_metadata(metadata=metadata)

        # Note: In case user added via prompt, we store the user's input before re-validating the final metadata.
        output_path = f"{output_path}{self.model_id}.json"
        self.store_metadata(output_path=output_path, metadata=metadata)
        logging.info(f"{self.model_id}: Local model's metadata is stored in: {output_path}")
        try:
            # Validation of the previously created metadata
            if self.validate_metadata(metadata): self.metadata = metadata
            logging.debug(f"{self.model_id}: Created local model's final validated metadata: {self.metadata}")

            # Preparation of package_path needed for testing generation of __init__.py and testing of import as package.
            print(f"{self.metadata}")
            package_path = Path(self.metadata[self.model_id][CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_PACKAGE_LINK])
            # Update package_link in case it points to a zip archive instead of a dir.
            package_path = Utils.unzip_and_return_unzipped_path(package_path)
            self.metadata[CONFIG_FILE_KEY_PACKAGE_LINK] = str(package_path)

            # Now we want to check if there is an __init__.py file inside the dir that the package_link points to.
            if not self.is_init_file_available(package_path=package_path):
                # No __init__.py file exists, so we need to create one to enable imports of package.
                # Also, the import as package is tested.
                self.create_and_test_init_file(package_path=package_path,
                                               path_to_script_w_generate_function=path_to_script_w_generate_function)
        except Exception as e:
            raise Exception(f"{self.model_id}: An error occurred, but your model metadata was stored for reuse. "
                            f"Find it here: {output_path}") from e

    def validate_model_id(self, model_id: str, max_chars: int = 30, min_chars: int = 13) -> bool:
        num_chars = len(model_id)
        assert num_chars <= max_chars, f"The model_id {model_id} is too large ({num_chars}). Please reduce to a maximum of {max_chars} characters. Format Convention: '00001_GANTYPE_MODALITY'"
        assert num_chars >= min_chars, f"The model_id {model_id} is too small ({num_chars}). Please reduce to a minimum of {min_chars} characters. Format Convention: '00001_GANTYPE_MODALITY'"
        for i in range(5):
            assert model_id[
                i].isdigit(), f"Your model_id's ({model_id}) character '{model_id[i]}' at position {i} is not a digit. The first 5 characters should be digits as in '00001_GANTYPE_MODALITY'. Please adjust."
        return True

    def validate_metadata(self, metadata: dict = None) -> bool:
        # Assert metadata not None and the existence of the most important entries of the metadata nested below model_id
        assert metadata is not None, f" {self.model_id}: Error validating metadata. metadata is None (metadata={metadata})."
        metadata = metadata[self.model_id]
        expected_key_list = (CONFIG_FILE_KEY_EXECUTION, CONFIG_FILE_KEY_SELECTION)
        assert all(keys in metadata for keys in
                   expected_key_list), f"{self.model_id}: Error validating metadata. metadata did not contain one of '{expected_key_list}'. Metadata : {metadata}"

        # Checking entries inside 'execution' dict
        metadata = metadata[CONFIG_FILE_KEY_EXECUTION]
        expected_key_list = (
            CONFIG_FILE_KEY_PACKAGE_LINK, CONFIG_FILE_KEY_MODEL_EXTENSION, CONFIG_FILE_KEY_PACKAGE_NAME,
            CONFIG_FILE_KEY_MODEL_NAME, CONFIG_FILE_KEY_DEPENDENCIES, CONFIG_FILE_KEY_GENERATE)
        assert all(keys in metadata for keys in
                   expected_key_list), f"{self.model_id}: Error validating metadata. metadata did not contain one of '{expected_key_list}'. Metadata : {metadata}"

        # Checking if package link points to file or folder.
        package_path = Path(metadata[CONFIG_FILE_KEY_PACKAGE_LINK])
        assert package_path.exists() and (
                package_path.is_file() or package_path.is_dir()), f"{self.model_id}: Error validating metadata. The package link ({package_path}) you provided does not point to a file nor a folder."

        # Checking if package name is present
        package_name = metadata[CONFIG_FILE_KEY_PACKAGE_NAME]
        assert package_name is not None and package_name != "", f"{self.model_id}: Error validating metadata. The package name ({package_name}) is either not defined or an empty string. Please revise."

        # Checking if there is a weights/checkpoint (model name + model extension) file inside the package link if the latter is folder not zip.
        if package_path.is_dir():
            weights_path = Path(
                package_path / f"{metadata[CONFIG_FILE_KEY_MODEL_NAME]}{metadata[CONFIG_FILE_KEY_MODEL_EXTENSION]}")
        assert weights_path.is_file(), f"{self.model_id}: Error validating metadata. There was no model (weights) file found in {weights_path}. Please revise."

        # checking entries inside 'execution.generate_method' dict
        metadata = metadata[CONFIG_FILE_KEY_GENERATE]
        assert CONFIG_FILE_KEY_GENERATE_ARGS in metadata, f"{self.model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_GENERATE_ARGS}'. Metadata: {metadata}"

        # checking entries inside 'execution.generate_method.args' dict
        metadata = metadata[CONFIG_FILE_KEY_GENERATE_ARGS]
        assert CONFIG_FILE_KEY_GENERATE_ARGS_BASE in metadata, f"{self.model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_GENERATE_ARGS_BASE}'. Metadata: {metadata}"

        # checking entries inside 'execution.generate_method.args.base' dict
        metadata = metadata[CONFIG_FILE_KEY_GENERATE_ARGS_BASE]
        expected_key_list = (CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE, CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES,
                             CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH, CONFIG_FILE_KEY_GENERATE_ARGS_SAVE_IMAGES)
        assert all(keys in metadata for keys in
                   expected_key_list), f"{self.model_id}: Error validating metadata. metadata did not contain one of '{expected_key_list}'. Metadata : {metadata}"
        return True

    def create_metadata_from_path(self, metadata_path: str) -> dict:
        if Path(metadata_path).is_file():
            return Utils.read_in_json(path_as_string=metadata_path)
        else:
            raise FileNotFoundError(
                f"No metadata json file was found in the path you provided ({metadata_path}). Please adjust or set to None.")

    def create_metadata(self, package_link: str = None, package_name: str = None, model_name: str = None,
                        model_extension: str = None,
                        generate_method_name: str = None, dependencies: list = [], image_size: list = []) -> dict:
        # Using the metadata template for adherence to data structure.
        metadata = self.metadata_template[self.model_id][CONFIG_FILE_KEY_EXECUTION]
        metadata.update({CONFIG_FILE_KEY_PACKAGE_LINK: package_link})
        metadata.update({CONFIG_FILE_KEY_PACKAGE_NAME: package_name})
        metadata.update({CONFIG_FILE_KEY_MODEL_NAME: model_name})
        metadata.update({CONFIG_FILE_KEY_MODEL_EXTENSION: model_extension})
        metadata.update({CONFIG_FILE_KEY_DEPENDENCIES: dependencies})
        metadata.update({CONFIG_FILE_KEY_IMAGE_SIZE: image_size})
        metadata[CONFIG_FILE_KEY_GENERATE][CONFIG_FILE_KEY_GENERATE_NAME] = generate_method_name
        metadata_final = self.metadata_template
        metadata_final[self.model_id].update({CONFIG_FILE_KEY_EXECUTION: metadata})
        logging.info(f"The following metadata was automatically created based on your input: {metadata_final}")
        return metadata_final

    @staticmethod
    def load_metadata_template(path_to_metadata_template: str = None, model_id: str = None):
        if path_to_metadata_template is None:
            path_to_metadata_template = Path(f"{CONFIG_FILE_FOLDER}/{CONFIG_TEMPLATE_FILE_NAME_AND_EXTENSION}")
        metadata_template = Utils.read_in_json(path_as_string=path_to_metadata_template)
        if model_id is not None:
            # Replacing the placeholder id of template with model_id
            metadata_template[model_id] = metadata_template[list(metadata_template)[0]]
            del metadata_template[list(metadata_template)[0]]
        return metadata_template

    def store_metadata(self, output_path: str = "config/", metadata: dict = None):
        if metadata is None:
            metadata = self.metadata
        logging.debug(f"{self.model_id}: Metadata before storing: {metadata}")
        Utils.store_dict_as(dictionary=metadata, extension=".json", output_path=output_path)

    def is_key_value_set_or_dict(self, key: str, metadata: dict, nested_key) -> bool:
        if metadata.get(key) is None or metadata.get(key) == "" or (
                isinstance(metadata.get(key), list) and not metadata.get(key)) or isinstance(metadata.get(key), dict):
            # Note: If metadata.get(key) is referencing a dict, we always want to go inside the dict and add values.
            return False
        else:
            logging.debug(
                f"{self.model_id}: Key value pair ({key}:{metadata.get(key)}) already exists in metadata for key "
                f"'{nested_key}'. Not prompting user to insert value for this key.")
            return True

    def _recursively_fill_metadata(self, metadata_template: dict = None, metadata: dict = {},
                                   nested_key: str = '') -> dict:
        if metadata_template is None:
            metadata_template = self.metadata_template
        # Prompt user for optional metadata input
        retrieved_nested_key = nested_key
        for key in metadata_template:
            # nested_key to know where we are inside the metadata dict.
            nested_key = key if retrieved_nested_key == '' else f"{retrieved_nested_key}.{key}"
            if not self.is_key_value_set_or_dict(key=key, metadata=metadata, nested_key=nested_key):
                value_template = metadata_template.get(key)
                if value_template is None:
                    input_value = input(
                        f"{self.model_id}: Please enter value of type float or int for your model for key '{nested_key}': ")
                    try:
                        value_assigned = float(input_value.replace(",", "."))
                    except ValueError:
                        value_assigned = int(input_value) if input_value.isdigit() else None
                elif isinstance(value_template, list):
                    input_value = input(
                        f"{self.model_id}: Please enter a comma-separated list of values for your model for key: '{nested_key}': ")
                    value_assigned = list(input_value) if input_value != '' else []
                elif isinstance(value_template, str):
                    value_assigned = str(
                        input(
                            f"{self.model_id}: Please enter value of type string for your model for key '{nested_key}': "))
                elif isinstance(value_template, dict):
                    if len(value_template) == 0:
                        # If dict is empty, no recursion. Instead, we ask the user directly for input.
                        iterations = int(input(
                            f"{self.model_id}: How many key-value pairs do you want to nest below key '{nested_key}' "
                            f"in your model's metadata. Type a number: ") or "0")
                        nested_metadata: dict = {}
                        for i in range(iterations):
                            nested_key_input = str(input(f"{self.model_id}: Enter key {i + 1}: "))
                            nested_value_input = input(
                                f"{self.model_id}: For key{i + 1}={nested_key_input}, enter value: ")
                            nested_metadata.update({nested_key_input: nested_value_input})
                        value_assigned = nested_metadata
                    else:
                        # From metadata, get the nested dict below the key. If metadata has no nested dict, get the
                        # template's nested dict instead, which is stored in value_template
                        temp_metadata = metadata.get(key) if metadata.get(key) is not None else value_template
                        # Filling nested dicts via recursion. value_assigned is of type dict in this case.
                        value_assigned = self._recursively_fill_metadata(metadata_template=value_template,
                                                                         nested_key=nested_key, metadata=temp_metadata)
                logging.debug(f"{self.model_id}: You provided this key-value pair: {key}={value_assigned}")
                metadata.update({key: value_assigned})
        return metadata

    def is_init_file_available(self, package_path: str) -> bool:
        if Path(package_path).is_dir():
            return Utils.is_file_in(folder_path=package_path, filename=INIT_PY_FILE)
        else:
            raise Exception(
                f"{self.model_id}: Your package path ({package_path}) does not point to a directory nor to a zip file. Please adjust and try again.")

    def create_and_test_init_file(self, path_to_script_w_generate_function: str, package_path: str):
        # Check absolute and relative paths for script that contains generate function.
        if path_to_script_w_generate_function is None or not (
                Path(path_to_script_w_generate_function).is_file() or Path(
            f'{package_path}/{path_to_script_w_generate_function}').is_file()):
            raise Exception(
                f"{self.model_id}: path_to_script_w_generate_function is '{path_to_script_w_generate_function}'. "
                f"To automatically create an __init__.py file inside your package_path ({package_path}), "
                f"you need to provide an absolute path to a script that contains a synthetic data generation "
                f"function.")

        if Utils.is_file_in(filename=INIT_PY_FILE, folder_path=package_path):
            logging.warning(
                f"{self.model_id}: The file {INIT_PY_FILE} is already in {package_path}. Adding import statements "
                f"to it. Please revise file '{INIT_PY_FILE}'.")
        # Get the module path information needed to specify import of generate function in to-be-generated __init__.py
        # Remove package_path in case path_to_script_w_generate_function is absolute path. Also, change / to .
        module_import_path = "." + path_to_script_w_generate_function.replace(f'{package_path}/', '').replace(
            f'{package_path}', '').replace('/', '.').replace('\\', '.').replace('.py', '')

        # Create __init__.py file inside the package
        f = open(f'{package_path}/{INIT_PY_FILE}', "w")
        f.write("\n")
        f.write(f"from {module_import_path} import *")
        #f.write(f"import .{module_import_path}")
        f.write("\n")
        f.close()

        # Validation: Import module as python library to check if generate function is inside the
        # path_to_script_w_generate_function python file and no errors occur.
        try:
            module_name = Path(package_path).name
            sys.path.insert(1, str(package_path).replace(module_name, ""))
            importlib.import_module(name=module_name)
        except Exception as e:
            raise Exception(f"{self.model_id}: Error while testing the import of this module. Was the file "
                            f"'{path_to_script_w_generate_function}' imported into {package_path}/{target_filename}? Another source of error is that the "
                            f"generate function may not be inside the file '{path_to_script_w_generate_function}'. Or, "
                            f"the import path '{module_import_path}' in {INIT_PY_FILE} might be broken? Please revise and "
                            f"try again.") from e

    def __str__(self):
        return json.dumps(
            {'model_id': self.model_id, 'metadata': self.metadata})

    def __repr__(self):
        return f'ModelMatchCandidate(model_id={self.model_id}, metadata={self.metadata})'

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
