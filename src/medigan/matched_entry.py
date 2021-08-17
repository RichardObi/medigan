# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
@author: Richard Osuala
BCN-AIM Lab 2021
Contact: richard.osuala@ub.edu
"""

# Import python native libs
from __future__ import absolute_import

import json


class MatchedEntry():
    """ Match entry: key or key-value pair that was matched."""

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
