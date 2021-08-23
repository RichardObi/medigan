# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" Config manager class that downloads, ingests, parses, and prepares the config information for all models.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
.. codeauthor:: Noussair Lazrak <lazrak.noussair@gmail.com>
"""

# Import python native libs
from __future__ import absolute_import

import json
# Import pypi libs
from pathlib import Path

# Import library internal modules
from .constants import CONFIG_FILE_NAME_AND_EXTENSION, CONFIG_FILE_URL, CONFIG_FILE_FOLDER
from .utils import Utils


class ConfigManager():
    """ConfigManager class."""

    def __init__(
            self, config_object: object = None, is_new_download_forced: bool = False
    ):
        self.config_object = config_object
        self.model_ids = []
        self.is_config_loaded = False
        self.load_config_file(is_new_download_forced=is_new_download_forced)

    def load_config_file(self, is_new_download_forced: bool = False) -> bool:
        """ Load a config file and return boolean flag indicating success of loading process.

        If the config file is not present in medigan.CONSTANTS.CONFIG_FILE_FOLDER, it is per default downloaded from
        the web resource specified in medigan.CONSTANTS.CONFIG_FILE_URL.

        Parameters
        ----------
        is_new_download_forced: bool
            Forces new download of config file even if the file has been downloaded before.

        Returns
        -------
        bool
            a boolean flag indicating true only if the config file was loaded successfully.
        """
        if self.config_object is None:
            assert Utils.mkdirs(
                path_as_string=CONFIG_FILE_FOLDER), f"The config folder was not found nor created in {CONFIG_FILE_FOLDER}."
            config_file_path = Path(f"{CONFIG_FILE_FOLDER}/{CONFIG_FILE_NAME_AND_EXTENSION}")
            if not Utils.is_file_located_or_downloaded(path_as_string=config_file_path, download_if_not_found=True,
                                                       download_link=CONFIG_FILE_URL,
                                                       is_new_download_forced=is_new_download_forced):
                raise FileNotFoundError(
                    f"The config file {CONFIG_FILE_NAME_AND_EXTENSION} was not found in {config_file_path} nor downloaded from {CONFIG_FILE_URL}.")
            self.config_object = Utils.read_in_json(path_as_string=config_file_path)
            self.model_ids = [config for config in self.config_object]
            self.is_config_loaded = True
        return self.is_config_loaded

    def get_config_by_id(self, model_id, config_key: str = None) -> dict:
        """ From config_manager, get and return the part of the config below a config_key for a specific model_id.

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
            a dictionary from the part of the config file corresponding to model_id and config_key.
        """
        config_dict = self.config_object[model_id]
        if config_key is not None:
            # Split the key string by "." to enable evaluation of keys that are in nested dicts
            config_key_split = config_key.split(".")
            for key in config_key_split:
                config_dict = config_dict[key]
        return config_dict

    def _validate_config_file(self):
        raise NotImplementedError

    def __str__(self):
        return json.dumps(self.config_object)

    def __repr__(self):
        return f'ConfigManager(model_ids={self.model_ids}, is_config_loaded={self.is_config_loaded})'

    def __len__(self):
        return len(self.config_object)

    def __getitem__(self, idx: int):
        raise NotImplementedError
