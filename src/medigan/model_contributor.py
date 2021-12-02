# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""Model contributor class that tests models, creates metadata entries, uploads and contributes them to medigan.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""

# Import python native libs
from __future__ import absolute_import

import logging
import shutil

# Import library internal modules
from .config_manager import ConfigManager
from .local_model import LocalModel

# Import pypi libs


class ModelContributor:
    """ `ModelContributor` class: Contributes a user's local model to the public medigan library"""

    def __init__(
            self,
            local_model: LocalModel = None,
            model_id: str = None,
            metadata: dict = None,
    ):
        if local_model is None:
            self.local_model = LocalModel(model_id=model_id, metadata=metadata)
            logging.debug(f"Initialized LocalModel instance: {self.local_model}")
        else:
            self.local_model = local_model

    def contribute(self):
        # TODO: Test the model
        # TODO: Create metadata
        # TODO: Prepare zip of model
        # TODO: Upload to Zenodo via API
        # TODO: Commit metadata to medigan-models repo
        # TODO: Pull request for new metadata in medigan-models repo
        pass

    def test_model(self, root_folder_path, ):
        # TODO:
        # Import
        pass

    def append_model_metadata_to_medigan_config(self):
        pass

    def create_config_pull_request(self):
        pass

    def zip_model(self, dir_path: str, output_filename: str = None):
        # TODO: Move to utils
        shutil.make_archive(output_filename, 'zip', dir_path)

    def upload_model(self):
        pass

    def __repr__(self):
        return f'ModelSelector()'

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
