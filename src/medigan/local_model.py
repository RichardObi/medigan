# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""LocalModel class that holds the information about a user's local, not yet contributed, generative model in medigan.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""

# Import python native libs
from __future__ import absolute_import
from pathlib import Path


import json
import logging

# Import library internal modules
from .matched_entry import MatchedEntry
from .config_manager import ConfigManager
from .utils import Utils
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

        if metadata is not None and self.validate_metadata(metadata=metadata, metadata_path=None): self.metadata = metadata


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


    def create_model_metadata(self, is_stored: bool = False, output_path: str="/config"):
        # TODO check if there is already a metadata file named by model_id where it should be (in /config)
        if self.validate_metadata(metadata_path=self.metadata_path):
            # TODO Warn user that valid metadata is already here. Should be deleted manually first if user wants to generate a new one.
            pass
        self.config_manager = new ConfigManager(use_config_template=True)
        metadata = self.config_manager.config_dict

        # TODO insert the known metadata into metadata template
        self.metadata = metadata

        # TODO store and write to disk
        if is_stored:
            self.store_metadata(output_path=output_path)

    def store_metadata(self, filetype='json', output_path="/config"):
        # TODO assert filetype != "json": Not yet implemented exception
        # TODO parse as json and store
        pass

    def create_model_init_function(self):
        # TODO: Check if there is a __init__.py file there. Except if generate_script_path is None.
        # TODO: Else: Import generate_method_name from generate script in generated __init__.py.
        pass


    def __str__(self):
        return json.dumps({'model_id': self.model_id, 'metadata': self.metadata, 'root_folder_path': self.root_folder_path})

    def __repr__(self):
        return f'ModelMatchCandidate(model_id={self.model_id}, metadata={self.metadata}, root_folder_path: {self.root_folder_path})'

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
