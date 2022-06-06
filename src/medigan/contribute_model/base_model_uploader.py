# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""Base Model uploader class that uploads models to medigan associated data storage services.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""

from __future__ import absolute_import


class BaseModelUploader:
    """`BaseModelUploader` class: Uploads user's model to third party storage to allow its inclusion into medigan

        TODO
    """

    def __init__(
        self,
        model_id: str,
        metadata: dict,
    ):
        self.model_id = model_id
        self.metadata = metadata

    ############################ UPLOAD ############################

    def push(self):
        """ TODO """

        raise NotImplementedError

    def __repr__(self):
        return f"BaseModelUploader(model_id={self.model_id}, metadata={self.metadata})"

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
