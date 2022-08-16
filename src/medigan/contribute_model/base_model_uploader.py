# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""Base Model uploader class that uploads models to medigan associated data storage services. """

from __future__ import absolute_import


class BaseModelUploader:
    """`BaseModelUploader` class: Uploads a user's model and metadata to third party storage to allow its inclusion into the medigan library.

    Parameters
    ----------
    model_id: str
        The generative model's unique id
    metadata: dict
        The model's corresponding metadata

    Attributes
    ----------
    model_id: str
        The generative model's unique id
    metadata: dict
        The model's corresponding metadata
    """

    def __init__(
        self,
        model_id: str,
        metadata: dict,
    ):
        self.model_id = model_id
        self.metadata = metadata

    def push(self):
        raise NotImplementedError

    def __repr__(self):
        return f"BaseModelUploader(model_id={self.model_id}, metadata={self.metadata})"

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
