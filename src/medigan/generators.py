# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
@author: Richard Osuala, Noussair Lazrak
BCN-AIM Lab 2021
Contact: richard.osuala@ub.edu
"""

# Import python native libs
from __future__ import absolute_import

from .config_manager import ConfigManager
# Import library internal modules
from .constants import CONFIG_FILE_KEY_EXECUTION, MODEL_ID
from .model_executor import ModelExecutor
from .model_selector import ModelSelector


# Import pypi libs


class Generators():
    """Generators is the main class of the medigan package.."""

    def __init__(
            self, initialize_all_models: bool = False,
    ):
        self.config_manager = ConfigManager()
        self.model_selector = ModelSelector(config_manager=self.config_manager)
        self.model_executors = []
        if initialize_all_models:
            self.add_all_model_executors()

    ############################ CONFIG MANAGER METHODS ############################

    def get_config_by_id(self, model_id, config_key: str = None) -> dict:
        return self.config_manager.get_config_by_id(model_id=model_id, config_key=config_key)

    ############################ MODEL SELECTOR METHODS ############################

    def get_selection_criteria_by_id(self, model_id: str) -> dict:
        return self.model_selector.get_selection_criteria_by_id(model_id=model_id)

    def get_selection_values_for_key(self, key: str, model_id: str = None) -> list:
        return self.model_selector.get_selection_values_for_key(key=key, model_id=model_id)

    def get_selection_values_for_key(self, key: str, model_id: str = None) -> list:
        return self.model_selector.get_selection_keys(model_id=model_id)

    def get_models_by_key_value_pair(self, key1: str, value1: str, is_case_sensitive: bool = False) -> list:
        return self.model_selector.get_models_by_key_value_pair(key1=key1, value1=value1,
                                                                is_case_sensitive=is_case_sensitive)

    def rank_models_by_performance(self, model_ids: list = None, metric: str = 'SSIM', order: str = "asc") -> list:
        return self.model_selector.rank_models_by_performance(model_ids=model_ids, metric=metric, order=order)

    def find_matching_models_by_values(self, values: list, target_values_operator: str = 'AND',
                                       are_keys_also_matched: bool = False, is_case_sensitive: bool = False) -> list:
        return self.model_selector.find_matching_models_by_values(values=values,
                                                                  target_values_operator=target_values_operator,
                                                                  are_keys_also_matched=are_keys_also_matched,
                                                                  is_case_sensitive=is_case_sensitive)

    def find_models_and_rank(self, values: list, target_values_operator: str = 'AND',
                             are_keys_also_matched: bool = False, is_case_sensitive: bool = False,
                             metric: str = 'SSIM', order: str = "asc") -> list:
        return self.model_selector.find_models_and_rank(values=values,
                                                        target_values_operator=target_values_operator,
                                                        are_keys_also_matched=are_keys_also_matched,
                                                        is_case_sensitive=is_case_sensitive,
                                                        metric=metric,
                                                        order=order)

    def find_models_rank_and_generate(self, values: list, target_values_operator: str = 'AND',
                                      are_keys_also_matched: bool = False, is_case_sensitive: bool = False,
                                      metric: str = 'SSIM', order: str = "asc", number_of_images: int = 30,
                                      output_path: str = None):
        ranked_models = self.model_selector.find_models_and_rank(values=values,
                                                                 target_values_operator=target_values_operator,
                                                                 are_keys_also_matched=are_keys_also_matched,
                                                                 is_case_sensitive=is_case_sensitive,
                                                                 metric=metric,
                                                                 order=order)
        if len(ranked_models) < 1:
            print(f'For your input, there were {len(ranked_models)} matching models, while at least 1 is needed. '
                  f'Please adjust your search value inputs {values} to find at least one match.')
        else:
            # Let's generate with the best-ranked model
            print(f'For your input, there were {len(ranked_models)} models found and ranked. '
                  f'The highest ranked model will now be used for generation: {ranked_models[0]}')
            highest_ranking_model_id = ranked_models[0][MODEL_ID]
            self.generate(model_id=highest_ranking_model_id, number_of_images=number_of_images, output_path=output_path)

    def find_model_and_generate(self, values: list, target_values_operator: str = 'AND',
                                are_keys_also_matched: bool = False, is_case_sensitive: bool = False,
                                number_of_images: int = 30, output_path: str = None):
        matching_models: list = self.model_selector.find_matching_models_by_values(values=values,
                                                                                   target_values_operator=target_values_operator,
                                                                                   are_keys_also_matched=are_keys_also_matched,
                                                                                   is_case_sensitive=is_case_sensitive)
        if len(matching_models) > 1:
            print(f'For your input, there were more than 1 matching model ({len(matching_models)}). '
                  f'Please choose one of the models (see model_ids below) or use find_models_rank_and_generate() instead.'
                  f'Alternatively, you may also further specify additional search values apart from the provided ones '
                  f'to find exactly one model: {values}. The matching models were the following: \n {matching_models}')
        elif len(matching_models) < 1:
            print(f'For your input, there were {len(matching_models)} matching models, while 1 is needed. '
                  f'Please adjust your search value inputs {values} to find at least one match.')
        else:
            # Exactly one matching model. Let's generate with this model
            print(f'For your input, there was {len(matching_models)} model matched. '
                  f'This model will now be used for generation: {matching_models}')
            matched_model_id = matching_models[0].model_id
            self.generate(model_id=matched_model_id, number_of_images=number_of_images, output_path=output_path)

    ############################ MODEL EXECUTOR METHODS ############################

    def add_all_model_executors(self):
        for model_id in self.config_manager.model_ids:
            execution_config = self.config_manager.get_config_by_id(model_id=model_id,
                                                                    config_key=CONFIG_FILE_KEY_EXECUTION)
            self._add_model_executor(model_id=model_id,
                                     execution_config=execution_config)

    def add_model_executor(self, model_id: str):
        if not self.is_model_executor_already_added(model_id):
            execution_config = self.config_manager.get_config_by_id(model_id=model_id,
                                                                    config_key=CONFIG_FILE_KEY_EXECUTION)
            self._add_model_executor(model_id=model_id, execution_config=execution_config)

    def _add_model_executor(self, model_id: str, execution_config: object):
        if not self.is_model_executor_already_added(model_id):
            model_executor = ModelExecutor(model_id=model_id, execution_config=execution_config,
                                           download_package=True)
            self.model_executors.append(model_executor)

    def is_model_executor_already_added(self, model_id) -> bool:
        model_executor = self.find_model_executor_by_id(model_id=model_id)
        if model_executor is None:
            print(f"{model_id}: The model has not yet been added to the model_executor list.")
            return False
        return True

    def find_model_executor_by_id(self, model_id: str) -> ModelExecutor:
        for idx, model_executor in enumerate(self.model_executors):
            if model_executor.model_id == model_id:
                return model_executor
        return None

    def generate(self, model_id: str, number_of_images: int = 30, output_path: str = None):
        model_executor = self.find_model_executor_by_id(model_id=model_id)
        if model_executor is None:
            try:
                self.add_model_executor(model_id=model_id)
                model_executor = self.find_model_executor_by_id(model_id=model_id)
            except Exception as e:
                print(f"{model_id}: The model could not be added to model_executor list: {e}")
                raise e
        model_executor.generate(number_of_images=number_of_images, output_path=output_path)

    def get_model_as_dataloader(self, model_id: str):
        raise NotImplementedError

    ############################ OTHER METHODS ############################

    def __repr__(self):
        return f'Generators(model_ids={self.config_manager.model_ids}, model_executors={self.model_executors}, ' \
               f'model_selector: {self.model_selector})'

    def __len__(self):
        return len(self.model_executors)

    def __getitem__(self, idx: int):
        return self.model_executors[idx]
