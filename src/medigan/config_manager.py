# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
@author: Richard Osuala, Noussair Lazrak
BCN-AIM Lab 2021
Contact: richard.osuala@ub.edu
"""

# Import python native libs
from __future__ import absolute_import

# Import pypi libs
from pathlib import Path

# Import library internal modules
from .constants import CONFIG_FILE_NAME_AND_EXTENSION, CONFIG_FILE_URL, CONFIG_FILE_FOLDER
from .utils import Utils




class ConfigManager():
    """ConfigManager class."""

    def __init__(
            self, config_object: object = None
    ):
        self.config_object = config_object
        self.model_ids = []
        self._load_config_file()
        self._set_model_ids()
        # print(f"-------------")
        # print(f"{self.config_object}")

    def _load_config_file(self):
        if self.config_object is None:
            assert Utils.mkdirs(
                path_as_string=CONFIG_FILE_FOLDER), f"The config folder was not found nor created in {CONFIG_FILE_FOLDER}."
            config_file_path = Path(f"{CONFIG_FILE_FOLDER}/{CONFIG_FILE_NAME_AND_EXTENSION}")
            if not Utils.is_file_located_or_downloaded(path_as_string=config_file_path, download_if_not_found=True,
                                                       download_link=CONFIG_FILE_URL):
                raise FileNotFoundError(
                    f"The config file {CONFIG_FILE_NAME_AND_EXTENSION} was not found in {config_file_path} nor downloaded from {CONFIG_FILE_URL}.")
            self.config_object = Utils.read_in_json(path_as_string=config_file_path)

    def _set_model_ids(self):
        self.model_ids = [config for config in self.config_object]

    def print_model_config(self, model_id: str):
        print(f"{self.config_object[model_id]}")

    def get_config_by_id(self, model_id, config_key: str) -> object:
        """

        :rtype: object
        """
        return self.config_object[model_id][config_key]

    def _validate_config_file(self):
        raise NotImplementedError

    def __len__(self):
        return len(self.config_object)

    def __getitem__(self, idx: int):
        raise NotImplementedError
