# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""ModelMatchCandidate class that holds data to evaluate if a generative model matches against a search query.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
.. codeauthor:: Noussair Lazrak <lazrak.noussair@gmail.com>
"""

# Import python native libs
from __future__ import absolute_import

import json
import logging

# Import library internal modules
from .matched_entry import MatchedEntry


class ModelMatchCandidate:
    """ `ModelMatchCandidate` class: A prospectively matching model given the target values as model search params.

    Parameters
    ----------
    model_id: str
        The generative model's unique id
    target_values: list
        list of target values used to evaluate if a `ModelMatchCandidate` instance is a match
    target_values_operator: str
        the operator indicating the relationship between `values` in the evaluation of `ModelMatchCandidate` instances.
        Should be either "AND", "OR", or "XOR".
    is_case_sensitive: bool
        flag indicating whether the matching of `values` (and) keys should be case-sensitive
    are_keys_also_matched: bool
        flag indicating whether, apart from `values`, keys should also be matched
    is_match: bool
        flag indicating whether the `ModelMatchCandidate` instance is a match

    Attributes
    ----------
    model_id: str
        The generative model's unique id
    target_values: list
        list of target values used to evaluate if a `ModelMatchCandidate` instance is a match
    target_values_operator: str
        the operator indicating the relationship between `values` in the evaluation of `ModelMatchCandidate` instances.
        Should be either "AND", "OR", or "XOR".
    is_case_sensitive: bool
        flag indicating whether the matching of `values` (and) keys should be case-sensitive
    are_keys_also_matched: bool
        flag indicating whether, apart from values, keys should also be matched
    matched_entries: list
        contains iteratively added `MatchedEntry` class instances. Each of the `MatchedEntry` instances indicates a match
        between one of the user specified values in `self.target_values` and the selection config keys or `values` of the
        model of this `ModelMatchCandidate`.
    is_match: bool
        flag indicating whether the `ModelMatchCandidate` instance is a match
    """

    def __init__(
            self,
            model_id: str,
            target_values: list,
            target_values_operator: str = 'AND',
            is_case_sensitive: bool = False,
            are_keys_also_matched: bool = False,
            is_match: bool = False,
    ):
        # Descriptive variables
        self.model_id = model_id
        self.target_values = target_values
        self.target_values_operator = target_values_operator
        self.is_case_sensitive = is_case_sensitive
        self.are_keys_also_matched = are_keys_also_matched

        # Dynamically filled/changed variables
        self.matched_entries = []
        self.is_match = is_match

    def add_matched_entry(self, matched_entry: MatchedEntry) -> None:
        """ Add a `MatchedEntry` instance to the `matched_entries` list. """
        self.matched_entries.append(matched_entry)

    def get_all_matching_elements(self) -> list:
        """ Get the matching element from each of the `MatchedEntry` instances in the `matched_entries` list.

        Returns
        -------
        list
            list of all matching elements (i.e. string that matched a search value) from each `MatchedEntry` in
            `matched_entries`
        """

        matching_elements = []
        for matched_entry in self.matched_entries:
            matching_elements.append(matched_entry.matching_element)
        return matching_elements

    def check_if_is_match(self) -> bool:
        """ Evaluates whether the model represented by this instance is a match given search values and operator.

        The matching element from each `MatchEntry` of this instance ('self.matched_entries') are retrieved. To be a
        match, this instance ('self') needs to fulfill the requirement of the operator, which can be of value 'AND',
        or 'OR', or 'XOR'. For example, the default 'AND' requires that each search value ('self.target_values') has at
        least one corresponding `MatchEntry`, while in 'OR' only one of the search values needs to have been matched by a
        corresponding `MatchedEntry`.

        Returns
        -------
        bool
            flag that, only if True, indicates that this instance is a match given the search values and operator.
        """

        if self is not None and len(self) > 0:
            if self.target_values_operator == 'OR':
                self.is_match = True
            elif self.target_values_operator == 'AND':
                # removing duplicates via set conversion
                found_target_values = set(self.get_all_matching_elements())
                if all(elem in found_target_values for elem in self.target_values):
                    logging.debug(f'values: {self.target_values} AND found_target_values_list: {found_target_values}')
                    self.is_match = True
            elif self.target_values_operator == 'XOR':
                # removing duplicates via set conversion
                if len(list(set(self.get_all_matching_elements()).intersection(
                        self.target_values))) == 1:
                    self.is_match = True
        logging.debug(f"This ModelMatchCandidate was found to be a match: ({self}).")
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
