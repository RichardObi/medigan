# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" Config manager class that downloads, ingests, parses, and prepares the config information for all models.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
.. codeauthor:: Noussair Lazrak <lazrak.noussair@gmail.com>
"""

# Import python native libs
from __future__ import absolute_import

import json
import logging
from pathlib import Path

# Import library internal modules
from .constants import (
    CONFIG_FILE_FOLDER,
    CONFIG_FILE_KEY_DEPENDENCIES,
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
    CONFIG_FILE_NAME_AND_EXTENSION,
    CONFIG_FILE_URL,
    CONFIG_TEMPLATE_FILE_NAME_AND_EXTENSION,
    INIT_PY_FILE,
    TEMPLATE_FOLDER,
)
from .utils import Utils


class ConfigManager:
    """`ConfigManager` class: Downloads, loads and parses medigan's config json as dictionary.

    Parameters
    ----------
    config_dict: dict
        Optionally provides the config dictionary if already loaded and parsed in a previous process.
    is_new_download_forced: bool
        Flags, if True, that a new config file should be downloaded from the config link instead of parsing an existing
        file.

    Attributes
    ----------
    config_dict: dict
        Optionally provides the config dictionary if already loaded and parsed in a previous process.
    is_new_download_forced: bool
        Flags, if True, that a new config file should be downloaded from the config link instead of parsing an existing
        file.
    model_ids: list
        Lists the unique id's of the generative models specified in the `config_dict`
    is_config_loaded: bool
        Flags if the loading and parsing of the config file was successful (True) or not (False).
    """

    def __init__(self, config_dict: dict = None, is_new_download_forced: bool = False):
        self.config_dict = config_dict
        self.model_ids = []
        self.is_config_loaded = False
        self.load_config_file(is_new_download_forced=is_new_download_forced)

    def load_config_file(self, is_new_download_forced: bool = False) -> bool:
        """Load a config file and return boolean flag indicating success of loading process.

        If the config file is not present in `medigan.CONSTANTS.CONFIG_FILE_FOLDER`, it is per default downloaded from
        the web resource specified in `medigan.CONSTANTS.CONFIG_FILE_URL`.

        Parameters
        ----------
        is_new_download_forced: bool
            Forces new download of config file even if the file has been downloaded before.

        Returns
        -------
        bool
            a boolean flag indicating true only if the config file was loaded successfully.
        """
        if self.config_dict is None:
            assert Utils.mkdirs(
                path_as_string=CONFIG_FILE_FOLDER
            ), f"The config folder was not found nor created in {CONFIG_FILE_FOLDER}."
            config_file_path = Path(
                f"{CONFIG_FILE_FOLDER}/{CONFIG_FILE_NAME_AND_EXTENSION}"
            )
            try:
                if not Utils.is_file_located_or_downloaded(
                    path_as_string=config_file_path,
                    download_if_not_found=True,
                    download_link=CONFIG_FILE_URL,
                    is_new_download_forced=is_new_download_forced,
                ):
                    error_string = (
                        f"The config file {CONFIG_FILE_NAME_AND_EXTENSION} was not found in {config_file_path} "
                        f"nor downloaded from {CONFIG_FILE_URL}."
                    )
                    logging.error(error_string)
                    raise FileNotFoundError(error_string)
            except Exception as e:
                raise e
            self.config_dict = Utils.read_in_json(path_as_string=config_file_path)
            logging.debug(f"The parsed config dict: {self.config_dict} ")
            self.model_ids = [config for config in self.config_dict]
            logging.debug(f"The model_ids found in the config dict: {self.model_ids} ")
            self.is_config_loaded = True
        return self.is_config_loaded

    def get_config_by_id(self, model_id: str, config_key: str = None) -> dict:
        """From `config_manager`, get and return the part of the config below a config_key for a specific `model_id`.

        The key param can contain '.' (dot) separations to allow for retrieval of nested config keys such as
        'execution.generator.name'

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        config_key: str
            A key of interest present in the config dict

        Returns
        -------
        dict
            a dictionary from the part of the config file corresponding to `model_id` and `config_key`.
        """
        config_dict = self.config_dict[model_id]
        if config_key is not None:
            # Split the key string by "." to enable evaluation of keys that are in nested dicts
            config_key_split = config_key.split(".")
            for key in config_key_split:
                config_dict = config_dict[key]
        return config_dict

    def add_model_to_config(
        self,
        model_id: str,
        metadata: dict,
        metadata_file_path: str = "",
        overwrite_existing_metadata: bool = False,
        store_new_config: bool = True,
    ) -> bool:
        """TODO"""

        if not self.is_model_metadata_valid(
            model_id=model_id, metadata=metadata, metadata_file_path=metadata_file_path
        ):
            logging.debug(
                f"{model_id}: Metadata was not added to config. Reason: metadata was not valid. Please revise and try again."
            )
            return False
        if self.is_model_in_config and not overwrite_existing_metadata:
            logging.warning(
                f"{model_id}: Metadata was not added to coonfig. Reason: For {model_id} there is already an entry in the metadata and 'overwrite_existing_metadata' was set to {overwrite_existing_metadata}."
            )
            return False
        self.config_dict.update(metadata)
        if store_new_config:
            Utils.store_dict_as(
                dictionary=self.config_dict,
                output_path=f"{CONFIG_FILE_FOLDER}/{CONFIG_FILE_NAME_AND_EXTENSION}",
            )
            logging.info(
                f"{model_id}: Model metadata was added and config file ({CONFIG_FILE_FOLDER}/{CONFIG_FILE_NAME_AND_EXTENSION}) was successfully updated."
            )
        else:
            logging.info(
                f"{model_id}: Model metadata was successfully added. Note: config file ({CONFIG_FILE_FOLDER}/{CONFIG_FILE_NAME_AND_EXTENSION}) was NOT updated."
            )
        return True

    def is_model_in_config(self, model_id: str) -> bool:
        """TODO"""

        try:
            self.get_config_by_id(model_id)
        except KeyError as e:
            return False
        return True

    def is_model_metadata_valid(
        self,
        model_id: str,
        metadata: dict,
        is_local_model: bool = True,
        metadata_file_path: str = "",
    ) -> bool:
        """TODO"""

        try:
            # Assert metadata not None and the existence of the most important entries of the metadata nested below model_id
            assert (
                metadata is not None
            ), f" {model_id}: Error validating metadata. metadata is None (metadata={metadata})."
            assert (
                metadata[model_id] is not None
            ), f" {model_id}: Error validating metadata. metadata does not contain model_id ({model_id}). (metadata={metadata})."
            metadata = metadata[model_id]
            expected_key_list = (CONFIG_FILE_KEY_EXECUTION, CONFIG_FILE_KEY_SELECTION)
            assert all(
                keys in metadata for keys in expected_key_list
            ), f"{model_id}: Error validating metadata. metadata did not contain one of '{expected_key_list}'. Metadata : {metadata}"

            # Checking entries inside 'execution' dict
            metadata = metadata[CONFIG_FILE_KEY_EXECUTION]
            expected_key_list = (
                CONFIG_FILE_KEY_PACKAGE_LINK,
                CONFIG_FILE_KEY_MODEL_EXTENSION,
                CONFIG_FILE_KEY_PACKAGE_NAME,
                CONFIG_FILE_KEY_MODEL_NAME,
                CONFIG_FILE_KEY_DEPENDENCIES,
                CONFIG_FILE_KEY_GENERATE,
            )
            assert all(
                keys in metadata for keys in expected_key_list
            ), f"{model_id}: Error validating metadata. metadata did not contain one of '{expected_key_list}'. Metadata : {metadata}"

            # Checking if package name is present
            package_name = metadata[CONFIG_FILE_KEY_PACKAGE_NAME]
            assert (
                package_name is not None and package_name != ""
            ), f"{model_id}: Error validating metadata. The package name ({package_name}) is either not defined or an empty string. Please revise."

            package_path = Path(metadata[CONFIG_FILE_KEY_PACKAGE_LINK])
            if is_local_model:
                if not (package_path.exists() and package_path.is_file()):
                    # TODO: Optional additional validation: If the package path actually points to a valid zip, check if the expected model file can be found in that zip.
                    assert (
                        package_path.exists() and package_path.is_dir()
                    ), f"{model_id}: Error validating metadata. Your package path ({package_path}) does not exist. Please revise and make sure the entry for metadata field '{CONFIG_FILE_KEY_PACKAGE_LINK}' points to a valid folder or zip file containing your model."
            else:
                assert Utils.is_url_valid(
                    the_url=package_path
                ), f"{model_id}: Error validating metadata. The package_path is not a valid url {package_path}. Please revise."

            # checking entries inside 'execution.generate_method' dict
            metadata = metadata[CONFIG_FILE_KEY_GENERATE]
            assert (
                CONFIG_FILE_KEY_GENERATE_ARGS in metadata
            ), f"{model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_GENERATE_ARGS}'. Metadata: {metadata}"

            # checking entries inside 'execution.generate_method.args' dict
            metadata = metadata[CONFIG_FILE_KEY_GENERATE_ARGS]
            assert (
                CONFIG_FILE_KEY_GENERATE_ARGS_BASE in metadata
            ), f"{model_id}: Error validating metadata. It did not contain key '{CONFIG_FILE_KEY_GENERATE_ARGS_BASE}'. Metadata: {metadata}"

            # checking entries inside 'execution.generate_method.args.base' dict
            metadata = metadata[CONFIG_FILE_KEY_GENERATE_ARGS_BASE]
            expected_key_list = (
                CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE,
                CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES,
                CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH,
                CONFIG_FILE_KEY_GENERATE_ARGS_SAVE_IMAGES,
            )
            assert all(
                keys in metadata for keys in expected_key_list
            ), f"{model_id}: Error validating metadata. metadata did not contain one of '{expected_key_list}'. Metadata : {metadata}"
        except Exception as e:
            logging.info(f"Metadata for model '{model_id}' was not valid: {e}")
            return False
        return True

    def __str__(self):
        return json.dumps(self.config_dict)

    def __repr__(self):
        return f"ConfigManager(model_ids={self.model_ids}, is_config_loaded={self.is_config_loaded})"

    def __len__(self):
        return len(self.config_dict)

    def __getitem__(self, idx: int):
        return list(self.config_dict)[idx]
