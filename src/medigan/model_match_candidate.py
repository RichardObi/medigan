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

# Import library internal modules
from .matched_entry import MatchedEntry


class ModelMatchCandidate():
    """ ModelMatchCandidate class: A prospectively matching model given the target values as model search params."""

    def __init__(
            self,
            model_id: str,
            target_values_operator: str,
            target_values: list,
            is_case_sensitive: bool = False,
            are_keys_also_matched: bool = False,
            is_match: bool = False,
    ):
        # Descriptive variables
        self.model_id = model_id
        self.target_values_operator = target_values_operator
        self.is_case_sensitive = is_case_sensitive
        self.are_keys_also_matched = are_keys_also_matched
        self.target_values = target_values

        # Dynamically filled/changed variables
        self.matched_entries = []
        self.is_match = is_match

    def add_matched_entry(self, matched_entry: MatchedEntry):
        self.matched_entries.append(matched_entry)

    def get_all_matching_elements(self):
        matching_elements = []
        for matched_entry in self.matched_entries:
            matching_elements.append(matched_entry.matching_element)
        return matching_elements

    def check_if_is_match(self) -> bool:
        if self is not None and len(self) > 0:
            if self.target_values_operator == 'OR':
                self.is_match = True
            elif self.target_values_operator == 'AND':
                # removing duplicates via set conversion
                found_target_values = set(self.get_all_matching_elements())
                if all(elem in found_target_values for elem in self.target_values):
                    # print(f'values: {self.target_values} AND found_target_values_list: {found_target_values}')
                    self.is_match = True
            elif self.target_values_operator == 'XOR':
                # removing duplicates via set conversion
                if len(list(set(self.get_all_matching_elements()).intersection(
                        self.target_values))) == 1:
                    self.is_match = True
        return self.is_match

    def __str__(self):
        matched_entry_dicts = {f'{idx}': json.loads(str(match)) for idx, match in enumerate(self.matched_entries)}
        return json.dumps({'model_id': self.model_id, 'is_match': self.is_match, 'target_values': self.target_values,
                           'operator': self.target_values_operator, 'are_keys_also_matched': self.are_keys_also_matched,
                           'is_case_sensitive': self.is_case_sensitive, 'matched_entries': matched_entry_dicts})

    def __repr__(self):
        return f'ModelMatchCandidate(model_id={self.model_id}, is_match={self.is_match}, operator: {self.target_values_operator}, target_values={self.target_values})'

    def __len__(self):
        return len(self.matched_entries)

    def __getitem__(self, idx: int):
        return self.matched_entries[idx]
