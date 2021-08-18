# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
@author: Richard Osuala
BCN-AIM Lab 2021
Contact: richard.osuala@ub.edu
"""

# Import python native libs
from __future__ import absolute_import

# Import library internal modules
from .config_manager import ConfigManager
from .constants import MODEL_ID, CONFIG_FILE_KEY_SELECTION, CONFIG_FILE_KEY_PERFORMANCE
from .matched_entry import MatchedEntry
from .model_match_candidate import ModelMatchCandidate
from .utils import Utils


class ModelSelector():
    """ModelSelector class."""

    def __init__(
            self,
            config_manager: ConfigManager = None,
    ):
        if config_manager is None:
            self.config_manager = ConfigManager()
        else:
            self.config_manager = config_manager
        self.model_selection_dicts = []
        self._init_model_selector_data()

    def _init_model_selector_data(self):
        for model_id in self.config_manager.model_ids:
            selection_config = self.config_manager.get_config_by_id(model_id=model_id,
                                                                    config_key=CONFIG_FILE_KEY_SELECTION)
            model_selector_dict = {MODEL_ID: model_id, CONFIG_FILE_KEY_SELECTION: selection_config}
            self.model_selection_dicts.append(model_selector_dict)

    def get_selection_criteria_by_id(self, model_id: str, is_model_id_removed: bool = True) -> dict:
        for idx, selection_dict in enumerate(self.model_selection_dicts):
            if selection_dict[MODEL_ID] == model_id:
                if is_model_id_removed:
                    return selection_dict[CONFIG_FILE_KEY_SELECTION]
                else:
                    return selection_dict
        return None

    def get_selection_criteria_by_ids(self, model_ids: list = None, are_model_ids_removed: bool = True) -> list:
        # Create list of models that contain a value for the metric of interest
        selection_dict_list = []
        for idx, selection_dict in enumerate(self.model_selection_dicts):
            if model_ids is None or selection_dict[MODEL_ID] in model_ids:
                # if model_ids is None, we consider all models
                if are_model_ids_removed:
                    selection_dict_list.append(selection_dict[CONFIG_FILE_KEY_SELECTION])
                else:
                    selection_dict_list.append(selection_dict)
        return selection_dict_list

    def get_selection_keys(self, model_id: str = None) -> list:
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
        return key_list

    def get_selection_values_for_key(self, key: str, model_id: str = None) -> list:
        values_for_key = []
        if model_id is not None:
            selection_config = self.get_selection_criteria_by_id(model_id)
            values_for_key.append(selection_config[key])
        else:
            for selection_dict in self.model_selection_dicts:
                selection_config = selection_dict[CONFIG_FILE_KEY_SELECTION]
                values_for_key.append(selection_config[key])
        return values_for_key

    def find_models_and_rank(self, values: list, target_values_operator: str = 'AND',
                             are_keys_also_matched: bool = False, is_case_sensitive: bool = False,
                             metric: str = 'SSIM', order: str = "asc") -> list:
        matching_models = self.find_matching_models_by_values(values=values,
                                            target_values_operator=target_values_operator,
                                            are_keys_also_matched=are_keys_also_matched,
                                            is_case_sensitive=is_case_sensitive)
        matching_model_ids = [model.model_id for model in matching_models]
        print (f"matching_model_ids: {matching_model_ids}")
        return self.rank_models_by_performance(model_ids=matching_model_ids, metric=metric, order=order)

    def find_matching_models_by_values(self, values: list, target_values_operator: str = 'AND',
                                       are_keys_also_matched: bool = False, is_case_sensitive: bool = False) -> list:
        assert values is not None and len(values) > 0, \
            f'Please specify a list of values to search for. You specified: {values}.'
        matching_models = []
        if not is_case_sensitive:
            # Removing case-sensitivity search requirement by replacing with lowercase values list
            values = Utils.list_to_lowercase(target_list=values)
        for selection_dict in self.model_selection_dicts:
            selection_config = selection_dict[CONFIG_FILE_KEY_SELECTION]
            model_match_candidate = ModelMatchCandidate(model_id=selection_dict[MODEL_ID],
                                                        target_values_operator=target_values_operator,
                                                        is_case_sensitive=is_case_sensitive,
                                                        target_values=values,
                                                        are_keys_also_matched=are_keys_also_matched)
            model_match_candidate = self._recursive_search_for_values(search_dict=selection_config,
                                                                      model_match_candidate=model_match_candidate)
            if model_match_candidate.check_if_is_match():
                matching_models.append(model_match_candidate)
        return matching_models

    def _recursive_search_for_values(self, search_dict: dict, model_match_candidate: ModelMatchCandidate):
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
                    key_or_counter = counter
                elif isinstance(search_dict, dict):
                    key_or_counter = key
                if isinstance(search_dict[key_or_counter], dict):
                    # The value of the key is of type dict, we thus search recursively inside that dictionary
                    model_match_candidate = self._recursive_search_for_values(
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

    def rank_models_by_performance(self, model_ids: list = None, metric: str = 'SSIM', order: str = "asc"):
        model_metric_dict_list = []
        if model_ids is not None and len(model_ids) == 0:
            # empty model_ids list -> return empty list.
            return model_metric_dict_list
        # First split the metric string by "." to enable nested dict downstream performance task evaluation
        metric_key_split = metric.split(".")
        last_key = metric_key_split[len(metric_key_split) - 1]
        # First, get all selection criteria for the model_ids
        selection_dict_list = self.get_selection_criteria_by_ids(model_ids=model_ids, are_model_ids_removed=False)
        for selection_criteria in selection_dict_list:
            # Now, for each model, we want to get the respective value for the metric
            try:
                # Maybe remove the case-sensitivity for metric here.
                metric_value = selection_criteria[CONFIG_FILE_KEY_SELECTION][CONFIG_FILE_KEY_PERFORMANCE]
                for key in metric_key_split:
                    metric_value = metric_value[key]
                if metric_value is not None:
                    # If metric value is None, the model is not added to the model_metric_dict_list
                    # Maybe add further validation of metric_value here, e.g., needs to be float, string to float conversion, etc.
                    model_id = selection_criteria[MODEL_ID]
                    model_metric_dict = {MODEL_ID: model_id, last_key: metric_value}
                    model_metric_dict_list.append(model_metric_dict)
            except KeyError as e:
                # The model does not have the specified keys and, hence, has not been added to the model_metric_dict_list
                pass
        if order == 'asc':
            model_metric_dict_list.sort(key=lambda x: x.get(last_key))
        else:
            model_metric_dict_list.sort(key=lambda x: x.get(last_key), reverse=True)
        return model_metric_dict_list

    def get_models_by_key_value_pair(self, key1: str, value1: str, key2: str = None, value2: str = None) -> list:
        raise NotImplementedError

    def __repr__(self):
        return f'ModelSelector(model_ids={self.config_manager.model_ids})'

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
