# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" Model selection class that describes, finds, compares, and ranks generative models.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>,
"""

# Import python native libs
from __future__ import absolute_import

import logging

# Import library internal modules
from .config_manager import ConfigManager
from .constants import MODEL_ID, CONFIG_FILE_KEY_SELECTION, CONFIG_FILE_KEY_PERFORMANCE
from .matched_entry import MatchedEntry
from .model_match_candidate import ModelMatchCandidate
from .utils import Utils


class ModelSelector():
    """ `ModelSelector` class: Given a config dict, gets, searches, and ranks matching models.

    Parameters
    ----------
    config_manager: ConfigManager
        Provides the config dictionary, based on which models are selected and compared.

    Attributes
    ----------
    config_manager: ConfigManager
        Provides the config dictionary, based on which models are selected and compared.
    model_selection_dicts: list
        Contains a dictionary for each model id that consists of the `model_id` and the selection config of that model
    """

    def __init__(
            self,
            config_manager: ConfigManager = None,
    ):
        if config_manager is None:
            self.config_manager = ConfigManager()
            logging.debug(f"Initialized ConfigManager instance: {self.config_manager}")
        else:
            self.config_manager = config_manager
        self.model_selection_dicts = []
        self._init_model_selector_data()

    def _init_model_selector_data(self):
        """ Initialize class data structure: List of dicts containing two keys each: `model_id` and `selection`. """
        for model_id in self.config_manager.model_ids:
            selection_config = self.config_manager.get_config_by_id(model_id=model_id,
                                                                    config_key=CONFIG_FILE_KEY_SELECTION)
            model_selector_dict = {MODEL_ID: model_id, CONFIG_FILE_KEY_SELECTION: selection_config}
            self.model_selection_dicts.append(model_selector_dict)
        logging.debug(f"These were the available model selection dicts that were added to the ModelSelector: "
                      f"{self.model_selection_dicts}.")

    def get_selection_criteria_by_id(self, model_id: str, is_model_id_removed: bool = True) -> dict:
        """ Get and return the selection config dict for a specific `model_id`.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        is_model_id_removed: bool
            flag to to remove the `model_id` from first level of each dictionary.

        Returns
        -------
        dict
            a dictionary corresponding to the selection config of a model
        """
        for idx, selection_dict in enumerate(self.model_selection_dicts):
            if selection_dict[MODEL_ID] == model_id:
                if is_model_id_removed:
                    logging.debug(f"For model {model_id}, the following selection dicts was found:"
                                  f" {selection_dict[CONFIG_FILE_KEY_SELECTION]}.")
                    return selection_dict[CONFIG_FILE_KEY_SELECTION]
                else:
                    logging.debug(f"For model {model_id}, the following selection dicts was found:"
                                  f" {selection_dict}.")
                    return selection_dict
        return None

    def get_selection_criteria_by_ids(self, model_ids: list = None, are_model_ids_removed: bool = True) -> list:
        """ Get and return a list of selection config dicts for each of the specified `model_ids`.

        Parameters
        ----------
        model_ids: list
            A list of generative models' unique ids
        are_model_ids_removed: bool
            flag to remove the `model_ids` from first level of dictionary.

        Returns
        -------
        list
            a list of dictionaries each corresponding to the selection config of a model
        """
        # Create list of models that contain a value for the metric of interest
        selection_dict_list = []
        for idx, selection_dict in enumerate(self.model_selection_dicts):
            if model_ids is None or selection_dict[MODEL_ID] in model_ids:
                # if model_ids is None, we consider all models
                if are_model_ids_removed:
                    selection_dict_list.append(selection_dict[CONFIG_FILE_KEY_SELECTION])
                else:
                    selection_dict_list.append(selection_dict)
        logging.debug(f"The following selection dicts were found: {selection_dict_list}.")
        return selection_dict_list

    def get_selection_keys(self, model_id: str = None) -> list:
        """ Get and return all first level keys from the selection config dict for a specific `model_id`.

        Parameters
        ----------
        model_id: str
            The generative model's unique id

        Returns
        -------
        list
            a list containing the keys as strings of the selection config of the `model_id`.
        """

        key_list = []
        if model_id is not None:
            selection_config = self.get_selection_criteria_by_id(model_id)
            for key in selection_config:
                key_list.append(key)
        else:
            for selection_dict in self.model_selection_dicts:
                selection_config = selection_dict[CONFIG_FILE_KEY_SELECTION]
                for key in selection_config:
                    if key not in key_list:
                        key_list.append(key)
        logging.debug(f"For model {model_id}, the following selection keys were in its selection config: {key_list}.")
        return key_list

    def get_selection_values_for_key(self, key: str, model_id: str = None) -> list:
        """ Get and return the value of a specified key of the selection dict in the config for a specific `model_id`.

        The key param can contain '.' (dot) separations to allow for retrieval of nested config keys such as
        'execution.generator.name'

        Parameters
        ----------
        key: str
            The key in the selection dict
        model_id: str
            The generative model's unique id

        Returns
        -------
        list
            a list of the values that correspond to the key in the selection config of the `model_id`.
        """

        values_for_key = []
        if model_id is not None:
            selection_config = self.get_selection_criteria_by_id(model_id)
            values_for_key.append(selection_config[key])
        else:
            for selection_dict in self.model_selection_dicts:
                selection_config = selection_dict[CONFIG_FILE_KEY_SELECTION]
                # if applicable, split key by "." and get value in nested dict in selection_config
                selection_config = Utils.deep_get(base_dict=selection_config, key=key)
                values_for_key.append(selection_config)
        logging.debug(f"For key {key}, the following values were found across the models' selection "
                      f"dicts {values_for_key}.")
        return values_for_key

    def get_models_by_key_value_pair(self, key1: str, value1: str, is_case_sensitive: bool = False) -> list:
        """ Get and return a list of `model_id` dicts that contain the specified key value pair in their selection config.

        The key param can contain '.' (dot) separations to allow for retrieval of nested config keys such as
        'execution.generator.name'. If `key1` points to a list, any value in the list that matches value1` is accepted.

        Parameters
        ----------
        key1: str`
            The key in the selection dict
        value1: str
            The value in the selection dict that corresponds to key1
        is_case_sensitive: bool
            flag to evaluate keys and values with case sensitivity if set to True

        Returns
        -------
        list
            a list of the dictionaries each containing a model's `model_id` and the found key-value pair in the models config
        """

        model_dict_list = []
        for selection_dict in self.model_selection_dicts:
            is_model_match: bool = False
            # Now, for each model, we want to get the respective value for the key
            try:
                key_value = selection_dict[CONFIG_FILE_KEY_SELECTION]
                key_value = Utils.deep_get(base_dict=key_value, key=key1)
                if key_value is not None:
                    # If key value is None, the model is not added to the model
                    if isinstance(key_value, dict):
                        # If the value of the key is a dict, we cannot evaluate a dict and continue the loop.
                        continue
                    if isinstance(key_value, list):
                        # If the value of the key is a list, we check if the provided value1 is in that list.
                        # Convert list of arbitrary type to list of strings
                        key_value = list(map(str, key_value))
                        if not is_case_sensitive:
                            key_value = Utils.list_to_lowercase(key_value)
                            value1 = value1.lower()
                        if str(value1) in key_value:
                            is_model_match = True
                    else:
                        # If the value of the key is something else (str, float, int, etc), we check if equal to value1
                        if (str(key_value) == str(value1)) or (
                                not is_case_sensitive and str(key_value).lower() == str(value1).lower()):
                            is_model_match = True
            except KeyError as e:
                logging.debug(f"Model {selection_dict[MODEL_ID]} was discarded as it does not have the specified keys "
                              f"in its selection dict: {selection_dict}")
                pass
            if is_model_match:
                model_id = selection_dict[MODEL_ID]
                model_dict = {MODEL_ID: model_id, key1: value1}
                logging.debug(f"Model {model_id} was a match for the specified key value pair: {model_dict}")
                model_dict_list.append(model_dict)
        return model_dict_list

    def rank_models_by_performance(self, model_ids: list = None, metric: str = 'SSIM', order: str = "asc") -> list:
        """ Rank model based on a provided metric and return sorted list of model dicts.

        The metric param can contain '.' (dot) separations to allow for retrieval via nested metric config keys such as
        'downstream_task.CLF.accuracy'. If the value found for the metric key is of type list, then the largest value in
        the list is used for ranking if `order` is descending, while the smallest value is used if `order` is ascending.

        Parameters
        ----------
        model_ids: list
            only evaluate the model_ids in this list. If none, evaluate all available `model_ids`
        metric: str
            The key in the selection dict that corresponds to the metric of interest
        order: str
            the sorting order of the ranked results. Should be either "asc" (ascending) or "desc" (descending)

        Returns
        -------
        list
            a list of model dictionaries containing metric and `model_id`, sorted by `metric`.
        """

        model_metric_dict_list = []
        if model_ids is not None and len(model_ids) == 0:
            # empty model_ids list -> return empty list.
            return model_metric_dict_list
        # First, get all selection criteria for the model_ids
        selection_dict_list = self.get_selection_criteria_by_ids(model_ids=model_ids, are_model_ids_removed=False)
        for selection_dict in selection_dict_list:
            # Now, for each model, we want to get the respective value for the metric
            try:
                # Maybe remove the case-sensitivity for metric here.
                metric_value = selection_dict[CONFIG_FILE_KEY_SELECTION][CONFIG_FILE_KEY_PERFORMANCE]
                metric_value = Utils.deep_get(base_dict=metric_value, key=metric)
                if metric_value is not None :
                    # If metric value is None, the model is not added to the model_metric_dict_list
                    # TODO Maybe add further validation of metric_value here, e.g. string to float conversion, etc.
                    if isinstance(metric_value, list) and order == 'asc':
                        # Assumption: As order is ascending (smallest item at top of list), we want to get the
                        # smallest (=best) possible value from our metric_value list.
                        metric_value = min(metric_value)
                    elif isinstance(metric_value, list):
                        # Assumption: As order is descending (largest item at top of list), we want to get the
                        # largest (=best) possible value from our metric_value list.
                        metric_value = max(metric_value)
                    model_id = selection_dict[MODEL_ID]
                    model_metric_dict = {MODEL_ID: model_id, metric: metric_value}
                    logging.debug(f"Model {model_id} was a match for the specified metric value: {model_metric_dict}")
                    model_metric_dict_list.append(model_metric_dict)
            except KeyError as e:
                logging.debug(f"Model {selection_dict[MODEL_ID]} was discarded as it does not have the specified keys "
                              f"in its selection dict: {selection_dict}")
                pass
        if order == 'asc':
            # ascending -> the smallest item appears at the top of the list
            model_metric_dict_list.sort(key=lambda x: x.get(metric))
        else:
            # descending -> the largest item appears at the top of the list
            model_metric_dict_list.sort(key=lambda x: x.get(metric), reverse=True)
        return model_metric_dict_list

    def find_models_and_rank(self, values: list, target_values_operator: str = 'AND',
                             are_keys_also_matched: bool = False, is_case_sensitive: bool = False,
                             metric: str = 'SSIM', order: str = "asc") -> list:
        """ Search for values (and keys) in model configs, rank results and return sorted list of model dicts.

        Parameters
        ----------
        values: list
            list of values used to search and find models corresponding to these `values`
        target_values_operator: str
            the operator indicating the relationship between `values` in the evaluation of model search results.
            Should be either "AND", "OR", or "XOR".
        are_keys_also_matched: bool
            flag indicating whether, apart from `values`, the keys in the model config should also be searchable
        is_case_sensitive: bool
            flag indicating whether the search for values (and) keys in the model config should be case-sensitive.
        metric: str
            The key in the selection dict that corresponds to the `metric` of interest
        order: str
            the sorting order of the ranked results. Should be either "asc" (ascending) or "desc" (descending)

        Returns
        -------
        list
            a list of the searched and matched model dictionaries containing `metric` and `model_id`, sorted by `metric`.
        """

        matching_models = self.find_matching_models_by_values(values=values,
                                                              target_values_operator=target_values_operator,
                                                              are_keys_also_matched=are_keys_also_matched,
                                                              is_case_sensitive=is_case_sensitive)
        matching_model_ids = [model.model_id for model in matching_models]
        logging.debug(f"matching_model_ids: {matching_model_ids}")
        return self.rank_models_by_performance(model_ids=matching_model_ids, metric=metric, order=order)

    def find_matching_models_by_values(self, values: list, target_values_operator: str = 'AND',
                                       are_keys_also_matched: bool = False, is_case_sensitive: bool = False) -> list:
        """ Search for values (and keys) in model configs and return a list of each matching `ModelMatchCandidate`.

        Uses `self.recursive_search_for_values` to recursively populate each `ModelMatchCandidate` with `MatchedEntry`
        instances. After populating, each `ModelMatchCandidate` is evaluated based on the provided
        `target_values_operator` and `values` list using `ModelMatchCandidate.check_if_is_match`.

        Parameters
        ----------
        values: list
            list of values used to search and find models corresponding to these values
        target_values_operator: str
            the operator indicating the relationship between `values` in the evaluation of model search results.
            Should be either "AND", "OR", or "XOR".
        are_keys_also_matched: bool
            flag indicating whether, apart from values, the keys in the model config should also be searchable
        is_case_sensitive: bool
            flag indicating whether the search for values (and) keys in the model config should be case-sensitive.

        Returns
        -------
        list
            a list of `ModelMatchCandidate` class instances each of which was successfully matched against the search
            values.
        """

        assert values is not None and len(values) > 0, \
            f'Please specify a list of values to search for. You specified: {values}.'
        matching_models = []
        if not is_case_sensitive:
            # Removing case-sensitivity search requirement by replacing with lowercase values list
            values = Utils.list_to_lowercase(target_list=values)
            logging.debug(f"Processed search values: {values}")
        for selection_dict in self.model_selection_dicts:
            selection_config = selection_dict[CONFIG_FILE_KEY_SELECTION]
            model_match_candidate = ModelMatchCandidate(model_id=selection_dict[MODEL_ID],
                                                        target_values_operator=target_values_operator,
                                                        is_case_sensitive=is_case_sensitive,
                                                        target_values=values,
                                                        are_keys_also_matched=are_keys_also_matched)
            model_match_candidate = self.recursive_search_for_values(search_dict=selection_config,
                                                                     model_match_candidate=model_match_candidate)
            if model_match_candidate.check_if_is_match():
                logging.debug(f"Found a matching ModelMatchCandidate: {model_match_candidate}")
                matching_models.append(model_match_candidate)
        return matching_models

    def recursive_search_for_values(self, search_dict: dict, model_match_candidate: ModelMatchCandidate):
        """ Do a recursive search to match values in the `search_dict` with values (and keys) in a model's config.

        The provided `ModelMatchCandidate` instance is recursively populated with `MatchedEntry` instances. A
        `MatchedEntry` instance contains a key-value pair found in the model's config that matches with one search
        term of interest.

        The search terms of interest are stored in `ModelMatchCandidate.target_values`. The model's selection config
        is provided in the 'search_dict'.

        To traverse the `search_dict`, the value for each key in the `search_dict` is retrieved.

        - If that value is of type dictionary, the function calls itself with that nested dictionary as new `search_dict`.

        - If that value is of type list, each value in the list is compared with each search term of interest in `ModelMatchCandidate.target_values`.

        - If the value of the `search_dict` is of another type (i.e. str), it is compared with each search term of interest in `ModelMatchCandidate.target_values`.

        Parameters
        ----------
        search_dict: dict
            contains keys and values from a model's config that are matched against a set of search values.
        model_match_candidate: ModelMatchCandidate
            a class instance representing a model to be prepared for evaluation (populated with `MatchedEntry` objects),
            as to whether it is a match given its search values (`self.target_values`).

        Returns
        -------
        list
            a `ModelMatchCandidate` class instance that has been populated with `MatchedEntry` class instances.
        """

        if search_dict is not None:
            counter = 0
            for key in search_dict:
                if model_match_candidate.are_keys_also_matched and not isinstance(search_dict, list):
                    # Treating the key as a match due to a matching string in target_values.
                    if not model_match_candidate.is_case_sensitive and key.lower() in model_match_candidate.target_values:
                        matched_entry = MatchedEntry(key='key', value=key, matching_element=key.lower())
                        model_match_candidate.add_matched_entry(matched_entry=matched_entry)
                    elif key in model_match_candidate.target_values:
                        matched_entry = MatchedEntry(key='key', value=key, matching_element=key)
                        model_match_candidate.add_matched_entry(matched_entry=matched_entry)
                if isinstance(search_dict, list):
                    # if we have a list we want the counter to get index position in list
                    key_or_counter = counter
                else:
                    # if we have something else i.e. a dict, we want to get the key to get nested dict
                    key_or_counter = key
                if isinstance(search_dict[key_or_counter], dict):
                    # The value of the key is of type dict, we thus search recursively inside that dictionary
                    model_match_candidate = self.recursive_search_for_values(
                        search_dict=search_dict[key_or_counter], model_match_candidate=model_match_candidate)
                elif isinstance(search_dict[key_or_counter], list):
                    for item in search_dict[key_or_counter]:
                        if not model_match_candidate.is_case_sensitive:
                            item = str(item).lower()
                        if str(item) in model_match_candidate.target_values:
                            matched_entry = MatchedEntry(key=key, value=item, matching_element=str(item))
                            model_match_candidate.add_matched_entry(matched_entry=matched_entry)
                else:
                    item = search_dict[key_or_counter]
                    if not model_match_candidate.is_case_sensitive:
                        item = str(item).lower()
                    if str(item) in model_match_candidate.target_values:
                        matched_entry = MatchedEntry(key=key, value=item, matching_element=str(item))
                        model_match_candidate.add_matched_entry(matched_entry=matched_entry)
                counter += counter
        return model_match_candidate

    def __repr__(self):
        return f'ModelSelector(model_ids={self.config_manager.model_ids})'

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
