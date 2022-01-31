# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""MatchedEntry class that represents one match of a key value pair of a model's config against a search query.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
.. codeauthor:: Noussair Lazrak <lazrak.noussair@gmail.com>
"""

# Import python native libs
from __future__ import absolute_import

import json


class MatchedEntry:
    """ `MatchedEntry` class: One target key-value pair that matches with a model's selection config.

    Parameters
    ----------
    key: str
        string that represents the matched key in model selection dict
    value
        represents the key's matched value in the model selection dict
    matching_element: str
        string that was used to match the search value

    Attributes
    ----------
    key: str
        string that represents the matched key in model selection dict
    value
        represents the key's matched value in the model selection dict
    matching_element: str
        string that was used to match the search value
    """

    def __init__(
            self,
            key: str,
            value,
            matching_element: str = None,
    ):
        self.key = key
        self.value = value
        if matching_element is None:
            self.matching_element = str(value)
        else:
            self.matching_element = matching_element

    def __str__(self):
        return json.dumps({'key': self.key, 'value': self.value, 'matching_element': self.matching_element})

    def __repr__(self):
        return f'MatchedEntry(key={self.key}, value={self.value}, matching_element={self.matching_element})'

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
