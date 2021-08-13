# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
@author: Richard Osuala, Noussair Lazrak
BCN-AIM Lab 2021
Contact: richard.osuala@ub.edu
"""

# Import python native libs
from __future__ import absolute_import

# Import pypi libs

# Import library internal modules
from .constants import CONFIG_FILE_KEY_EXECUTION, MODEL_ID, EXECUTOR
from .config_manager import ConfigManager
from .model_executor import ModelExecutor
from .model_selector import ModelSelector


class Generators():
    """Generators is the main class of the medigan package.."""

    def __init__(
            self, initialize_all_models: bool = False,
    ):
        self.config_manager = ConfigManager()
        self.model_selector = ModelSelector()
        self.model_executors = []
        if initialize_all_models:
            self.add_all_model_executors()

    def add_all_model_executors(self):
        for model_id in self.config_manager.model_ids:
            self.add_model_executor(model_id=model_id,
                                    execution_config=self.config_manager.get_config_by_id(model_id=model_id,
                                                                                          config_key=CONFIG_FILE_KEY_EXECUTION))

    def _add_model_executor(self, model_id: str, execution_config: object):
        if not self.is_model_executor_already_added(model_id):
            model_executor = ModelExecutor(model_id=model_id, execution_config=execution_config,
                                           download_package=True)
            model_executor_dict = {MODEL_ID: model_id, EXECUTOR: model_executor}
            self.model_executors.append(model_executor_dict)

    def add_model_executor(self, model_id: str):
        if not self.is_model_executor_already_added(model_id):
            self._add_model_executor(model_id=model_id,
                                    execution_config=self.config_manager.get_config_by_id(model_id=model_id,
                                                                                          config_key=CONFIG_FILE_KEY_EXECUTION))

    def is_model_executor_already_added(self, model_id) -> bool:
        model_executor = self.find_model_executor_by_id(model_id=model_id)
        if model_executor is not None:
            print(f"{model_id}: The model is already in model_executors at index position [{idx}].")
            return True
        return False

    def find_model_executor_by_id(self, model_id: str) -> ModelExecutor:
        for idx, model_executor_dict in enumerate(self.model_executors):
            if model_executor_dict[MODEL_ID] == model_id:
                return model_executor_dict[EXECUTOR]
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

    def find_matching_models(self):
        raise NotImplementedError

    def get_model_as_dataloader(self, model_id: str):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
