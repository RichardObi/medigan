# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""Github Model uploader class that uploads the metadata of a new model to medigan github repository.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""

from __future__ import absolute_import

import importlib
import zipfile
import json
import logging
import shutil
import sys
from pathlib import Path

import requests

from ..constants import (
    CONFIG_FILE_KEY_DEPENDENCIES,
    CONFIG_FILE_KEY_DESCRIPTION,
    CONFIG_FILE_KEY_EXECUTION,
    CONFIG_FILE_KEY_GENERATE,
    CONFIG_FILE_KEY_GENERATE_NAME,
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
    ZENODO_LINE_BREAK,
    ZENODO_API_URL,
)
from ..utils import Utils
from .base_model_uploader import BaseModelUploader

class GithubBaseModelUploader(BaseModelUploader):
    """`GithubBaseModelUploader` class: Pushes the metadata of a user's model to the medigan repo and initiates Pull request.

        TODO
    """

    def __init__(
            self,
        model_id,
        metadata,
    ):
        self.model_id = model_id
        self.metadata = metadata

    def push(self):
        """ TODO """

        # Users can get access_token from https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

        # TODO: Check if model has been added to config. If not, add it to config.
        # Important as the new config will be pushed to github PR later.

        # TODO Import libraries Gitpython and PyGithub
        # Info: https://stackoverflow.com/a/61533333

        # TODO git clone (Gitpython)
        # fork/clone medigan repo into local folder

        # TODO adjust global.json file
        # add the new model metadata to global.json (if not done already)

        # TODO git add (Gitpython)
        # add the new global.json to the medigan repo

        # TODO git commit (Gitpython)
        # commit the new global.json to the medigan repo

        # TODO git push (Gitpython)
        # create upstream branch on Github and push code there

        # TODO github PR (PyGithub)
        # create a Github pull request (PR) from forked repo to the original medigan repo (https://github.com/RichardObi/medigan)

        # TODO github assign_reviewer (PyGithub)
        # assign user 'RichardObi' as reviewer using https://pygithub.readthedocs.io/en/latest/github_objects/PullRequest.html#github.PullRequest.PullRequest.create_review_request

        raise NotImplementedError


    def __repr__(self):
        return f"GithubBaseModelUploader(model_id={self.model_id}, metadata={self.metadata})"

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
