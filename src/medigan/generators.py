# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" Base class providing user-library interaction methods for config management, and model selection and execution.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
.. codeauthor:: Noussair Lazrak <lazrak.noussair@gmail.com>
"""

# Import python native libs
from __future__ import absolute_import

import logging

# Import library internal modules
from .config_manager import ConfigManager
from .constants import CONFIG_FILE_KEY_EXECUTION, MODEL_ID
from .model_executor import ModelExecutor
from .model_selector import ModelSelector


# Import pypi libs


class Generators:
    """ `Generators` class: Contains medigan's public methods to facilitate users' automated sample generation workflows.

    Parameters
    ----------
    config_manager: ConfigManager
        Provides the config dictionary, based on which `model_ids` are retrieved and models are selected and executed
    model_selector: ModelSelector
        Provides model comparison, search, and selection based on keys/values in the selection part of the config dict
    model_executors: list
        List of initialized `ModelExecutor` instances that handle model package download, init, and sample generation
    initialize_all_models: bool
        Flag indicating, if True, that one `ModelExecutor` for each `model_id` in the config dict should be
        initialized triggered by creation of `Generators` class instance. Note that, if False, the `Generators` class
        will only initialize a `ModelExecutor` on the fly when need be i.e. when the generate method for the respective
        model is called.

    Attributes
    ----------
    config_manager: ConfigManager
        Provides the config dictionary, based on which model_ids are retrieved and models are selected and executed
    model_selector: ModelSelector
        Provides model comparison, search, and selection based on keys/values in the selection part of the config dict
    model_executors: list
        List of initialized `ModelExecutor` instances that handle model package download, init, and sample generation
    """

    def __init__(
            self,
            config_manager: ConfigManager = None,
            model_selector: ModelSelector = None,
            model_executors: list = None,
            initialize_all_models: bool = False
    ):
        if config_manager is None:
            self.config_manager = ConfigManager()
            logging.debug(f"Initialized ConfigManager instance: {self.config_manager}")
        else:
            self.config_manager = config_manager

        if model_selector is None:
            self.model_selector = ModelSelector(config_manager=self.config_manager)
            logging.debug(f"Initialized ModelSelector instance: {self.model_selector}")
        else:
            self.model_selector = model_selector

        if model_executors is None:
            self.model_executors = []
        else:
            self.model_executors = model_executors

        if initialize_all_models:
            self.add_all_model_executors()

    ############################ CONFIG MANAGER METHODS ############################

    def get_config_by_id(self, model_id: str, config_key: str = None) -> dict:
        """ Get and return the part of the config below a `config_key` for a specific `model_id`.

        The config_key parameters can be separated by a '.' (dot) to allow for retrieval of nested config keys, e.g,
        'execution.generator.name'

        This function calls an identically named function in a `ConfigManager` instance.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        config_key: str
            A key of interest present in the config dict

        Returns
        -------
        dict
            a dictionary from the part of the config file corresponding to `model_id` and `config_key`.
        """

        return self.config_manager.get_config_by_id(model_id=model_id, config_key=config_key)

    ############################ MODEL SELECTOR METHODS ############################

    def get_selection_criteria_by_id(self, model_id: str, is_model_id_removed: bool = True) -> dict:
        """ Get and return the selection config dict for a specific model_id.

        This function calls an identically named function in a `ModelSelector` instance.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        is_model_id_removed: bool
            flag to to remove the model_ids from first level of dictionary.

        Returns
        -------
        dict
            a dictionary corresponding to the selection config of a model
        """

        return self.model_selector.get_selection_criteria_by_id(model_id=model_id)

    def get_selection_criteria_by_ids(self, model_ids: list = None, are_model_ids_removed: bool = True) -> list:
        """ Get and return a list of selection config dicts for each of the specified model_ids.

        This function calls an identically named function in a `ModelSelector` instance.

        Parameters
        ----------
        model_ids: list
            A list of generative models' unique ids
        are_model_ids_removed: bool
            flag to remove the model_ids from first level of dictionary.

        Returns
        -------
        list
            a list of dictionaries each corresponding to the selection config of a model
        """

        return self.model_selector.get_selection_criteria_by_ids(model_ids=model_ids,
                                                                 are_model_ids_removed=are_model_ids_removed)

    def get_selection_values_for_key(self, key: str, model_id: str = None) -> list:
        """ Get and return the value of a specified key of the selection dict in the config for a specific model_id.

        The key param can contain '.' (dot) separations to allow for retrieval of nested config keys such as
        'execution.generator.name'

        This function calls an identically named function in a `ModelSelector` instance.

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

        return self.model_selector.get_selection_values_for_key(key=key, model_id=model_id)

    def get_selection_keys(self, model_id: str = None) -> list:
        """ Get and return all first level keys from the selection config dict for a specific model_id.

        This function calls an identically named function in a `ModelSelector` instance.

        Parameters
        ----------
        model_id: str
            The generative model's unique id

        Returns
        -------
        list
            a list containing the keys as strings of the selection config of the `model_id`.
        """

        return self.model_selector.get_selection_keys(model_id=model_id)

    def get_models_by_key_value_pair(self, key1: str, value1: str, is_case_sensitive: bool = False) -> list:
        """ Get and return a list of model_id dicts that contain the specified key value pair in their selection config.

        The key param can contain '.' (dot) separations to allow for retrieval of nested config keys such as
        'execution.generator.name'

        This function calls an identically named function in a `ModelSelector` instance.

        Parameters
        ----------
        key1: str
            The key in the selection dict
        value1: str
            The value in the selection dict that corresponds to key1
        is_case_sensitive: bool
            flag to evaluate keys and values with case sensitivity if set to True

        Returns
        -------
        list
            a list of the dictionaries each containing a models id and the found key-value pair in the models config
        """

        return self.model_selector.get_models_by_key_value_pair(key1=key1, value1=value1,
                                                                is_case_sensitive=is_case_sensitive)

    def rank_models_by_performance(self, model_ids: list = None, metric: str = 'SSIM', order: str = "asc") -> list:
        """ Rank model based on a provided metric and return sorted list of model dicts.

        The metric param can contain '.' (dot) separations to allow for retrieval of nested metric config keys such as
        'downstream_task.CLF.accuracy'

        This function calls an identically named function in a `ModelSelector` instance.

        Parameters
        ----------
        model_ids: list
            only evaluate the `model_ids` in this list. If none, evaluate all available `model_ids`
        metric: str
            The key in the selection dict that corresponds to the metric of interest
        order: str
            the sorting order of the ranked results. Should be either "asc" (ascending) or "desc" (descending)

        Returns
        -------
        list
            a list of model dictionaries containing metric and `model_id`, sorted by metric.
        """

        return self.model_selector.rank_models_by_performance(model_ids=model_ids, metric=metric, order=order)

    def find_matching_models_by_values(self, values: list, target_values_operator: str = 'AND',
                                       are_keys_also_matched: bool = False, is_case_sensitive: bool = False) -> list:
        """ Search for values (and keys) in model configs and return a list of each matching `ModelMatchCandidate`.

        This function calls an identically named function in a `ModelSelector` instance.

        Parameters
        ----------
        values: list
            list of values used to search and find models corresponding to these `values`
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

        return self.model_selector.find_matching_models_by_values(values=values,
                                                                  target_values_operator=target_values_operator,
                                                                  are_keys_also_matched=are_keys_also_matched,
                                                                  is_case_sensitive=is_case_sensitive)

    def find_models_and_rank(self, values: list, target_values_operator: str = 'AND',
                             are_keys_also_matched: bool = False, is_case_sensitive: bool = False,
                             metric: str = 'SSIM', order: str = "asc") -> list:
        """ Search for values (and keys) in model configs, rank results and return sorted list of model dicts.

        This function calls an identically named function in a `ModelSelector` instance.

        Parameters
        ----------
        values: list`
            list of values used to search and find models corresponding to these `values`
        target_values_operator: str
            the operator indicating the relationship between `values` in the evaluation of model search results.
            Should be either "AND", "OR", or "XOR".
        are_keys_also_matched: bool
            flag indicating whether, apart from values, the keys in the model config should also be searchable
        is_case_sensitive: bool
            flag indicating whether the search for values (and) keys in the model config should be case-sensitive.
        metric: str
            The key in the selection dict that corresponds to the metric of interest
        order: str
            the sorting order of the ranked results. Should be either "asc" (ascending) or "desc" (descending)

        Returns
        -------
        list
            a list of the searched and matched model dictionaries containing metric and model_id, sorted by metric.
        """
        ranked_models = []
        matching_models = self.model_selector.find_matching_models_by_values(values=values,
                                                                             target_values_operator=target_values_operator,
                                                                             are_keys_also_matched=are_keys_also_matched,
                                                                             is_case_sensitive=is_case_sensitive)
        if len(matching_models) < 1:
            logging.warning(
                f'For your input, there were {len(matching_models)} matching models, while at least 1 is needed. '
                f'Please adjust either your metric your search value inputs {values} to find at least one match.')
        else:
            matching_model_ids = [model.model_id for model in matching_models]
            logging.debug(f"matching_model_ids: {matching_model_ids}")
            ranked_models = self.model_selector.rank_models_by_performance(model_ids=matching_model_ids, metric=metric,
                                                                           order=order)
            if len(ranked_models) < 1:
                logging.warning(
                    f'None ({len(ranked_models)}) of the {len(matching_model_ids)} found matching models, had a valid metric entry for {metric}. '
                    f'Please adjust your metric to enable ranking of the found models.')
        return ranked_models

    def find_models_rank_and_generate(self, values: list, target_values_operator: str = 'AND',
                                      are_keys_also_matched: bool = False, is_case_sensitive: bool = False,
                                      metric: str = 'SSIM', order: str = "asc", num_samples: int = 30,
                                      output_path: str = None, is_gen_function_returned: bool = False, **kwargs):
        """ Search for values (and keys) in model configs, rank results to generate samples with highest ranked model.

        Parameters
        ----------
        values: list
            list of values used to search and find models corresponding to these `values`
        target_values_operator: str
            the operator indicating the relationship between `values` in the evaluation of model search results.
            Should be either "AND", "OR", or "XOR".
        are_keys_also_matched: bool
            flag indicating whether, apart from values, the keys in the model config should also be searchable
        is_case_sensitive: bool
            flag indicating whether the search for values (and) keys in the model config should be case-sensitive.
        metric: str
            The key in the selection dict that corresponds to the metric of interest
        order: str
            the sorting order of the ranked results. Should be either "asc" (ascending) or "desc" (descending)
        num_samples: int
            the number of samples that will be generated
        output_path: str
            the path as str to the output folder where the generated samples will be stored
        is_gen_function_returned: bool
            flag indicating whether, instead of generating samples, the sample generation function will be returned
        **kwargs
            arbitrary number of keyword arguments passed to the model's sample generation function

        Returns
        -------
        None
            However, if `is_gen_function_returned` is True, it returns the internal generate function of the model.
        """
        ranked_models = self.find_models_and_rank(values=values,
                                                  target_values_operator=target_values_operator,
                                                  are_keys_also_matched=are_keys_also_matched,
                                                  is_case_sensitive=is_case_sensitive, metric=metric, order=order)

        assert ranked_models is not None and len(ranked_models) > 0, \
            f'None of the models fulfilled both, the matching (values: {values}) AND ' \
            f'ranking (metric: {metric}) criteria you provided.'

        # Get the ID of the highest ranking model to generate() with that model
        highest_ranking_model_id = ranked_models[0][MODEL_ID]

        # Let's generate with the best-ranked model
        logging.info(f'For your input, there were {len(ranked_models)} models found and ranked. '
                     f'The highest ranked model ({highest_ranking_model_id}) will now be used for generation: '
                     f'{ranked_models[0]}')

        return self.generate(model_id=highest_ranking_model_id, num_samples=num_samples,
                             output_path=output_path,
                             is_gen_function_returned=is_gen_function_returned, **kwargs)

    def find_model_and_generate(self, values: list, target_values_operator: str = 'AND',
                                are_keys_also_matched: bool = False, is_case_sensitive: bool = False,
                                num_samples: int = 30, output_path: str = None, is_gen_function_returned: bool = False,
                                **kwargs):
        """ Search for values (and keys) in model configs to generate samples with the found model.

        Note that the number of found models should be ==1. Else no samples will be generated and a error is logged to
        console.

        Parameters
        ----------
        values: list
            list of values used to search and find models corresponding to these `values`
        target_values_operator: str
            the operator indicating the relationship between `values`  in the evaluation of model search results.
            Should be either "AND", "OR", or "XOR".
        are_keys_also_matched: bool
            flag indicating whether, apart from values, the keys in the model config should also be searchable
        is_case_sensitive: bool
            flag indicating whether the search for values (and) keys in the model config should be case-sensitive.
        num_samples: int
            the number of samples that will be generated
        output_path: str
            the path as str to the output folder where the generated samples will be stored
        is_gen_function_returned: bool
            flag indicating whether, instead of generating samples, the sample generation function will be returned
        **kwargs
            arbitrary number of keyword arguments passed to the model's sample generation function

        Returns
        -------
        None
            However, if `is_gen_function_returned` is True, it returns the internal generate function of the model.
        """

        matching_models: list = self.model_selector.find_matching_models_by_values(values=values,
                                                                                   target_values_operator=target_values_operator,
                                                                                   are_keys_also_matched=are_keys_also_matched,
                                                                                   is_case_sensitive=is_case_sensitive)
        if len(matching_models) > 1:
            logging.error(f'For your input, there were more than 1 matching model ({len(matching_models)}). '
                          f'Please choose one of the models (see model_ids below) or use find_models_rank_and_generate() instead.'
                          f'Alternatively, you may also further specify additional search values apart from the provided ones '
                          f'to find exactly one model: {values}. The matching models were the following: \n {matching_models}')
        elif len(matching_models) < 1:
            logging.error(f'For your input, there were {len(matching_models)} matching models, while 1 is needed. '
                          f'Please adjust your search value inputs {values} to find at least one match.')
        else:
            # Exactly one matching model. Let's generate with this model
            logging.info(f'For your input, there was {len(matching_models)} model matched. '
                         f'This model will now be used for generation: {matching_models}')
            matched_model_id = matching_models[0].model_id
            return self.generate(model_id=matched_model_id, num_samples=num_samples, output_path=output_path,
                                 is_gen_function_returned=is_gen_function_returned, **kwargs)

    ############################ MODEL EXECUTOR METHODS ############################

    def add_all_model_executors(self):
        """ Add `ModelExecutor` class instances for all models available in the config.

        Returns
        -------
        None
        """

        for model_id in self.config_manager.model_ids:
            execution_config = self.config_manager.get_config_by_id(model_id=model_id,
                                                                    config_key=CONFIG_FILE_KEY_EXECUTION)
            self._add_model_executor(model_id=model_id,
                                     execution_config=execution_config)

    def add_model_executor(self, model_id: str):
        """ Add one `ModelExecutor` class instance corresponding to the specified `model_id`.

        Parameters
        ----------
        model_id: str
            The generative model's unique id

        Returns
        -------
        None
        """

        if not self.is_model_executor_already_added(model_id):
            execution_config = self.config_manager.get_config_by_id(model_id=model_id,
                                                                    config_key=CONFIG_FILE_KEY_EXECUTION)
            self._add_model_executor(model_id=model_id, execution_config=execution_config)

    def _add_model_executor(self, model_id: str, execution_config: dict):
        """ Add one `ModelExecutor` class instance corresponding to the specified `model_id` and `execution_config`.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        execution_config: dict
            The part of the config below the 'execution' key

        Returns
        -------
        None
        """

        if not self.is_model_executor_already_added(model_id):
            model_executor = ModelExecutor(model_id=model_id, execution_config=execution_config,
                                           download_package=True)
            self.model_executors.append(model_executor)

    def is_model_executor_already_added(self, model_id) -> bool:
        """ Check whether the `ModelExecutor` instance of this model_id is already in `self.model_executors` list.

        Parameters
        ----------
        model_id: str
            The generative model's unique id

        Returns
        -------
        bool
            indicating whether this `ModelExecutor` had been already previously added to `self.model_executors`
        """

        if self.find_model_executor_by_id(model_id=model_id) is None:
            logging.debug(f"{model_id}: The model has not yet been added to the model_executor list.")
            return False
        return True

    def find_model_executor_by_id(self, model_id: str) -> ModelExecutor:
        """ Find and return the `ModelExecutor` instance of this model_id in the `self.model_executors` list.

        Parameters
        ----------
        model_id: str
            The generative model's unique id

        Returns
        -------
        ModelExecutor
            `ModelExecutor` class instance corresponding to the `model_id`
        """

        for idx, model_executor in enumerate(self.model_executors):
            if model_executor.model_id == model_id:
                return model_executor
        return None

    def get_model_executor(self, model_id: str) -> ModelExecutor:
        """ Add and return the `ModelExecutor` instance of this model_id from the `self.model_executors` list.

        Relies on `self.add_model_executor` and `self.find_model_executor_by_id` functions.

        Parameters
        ----------
        model_id: str
            The generative model's unique id

        Returns
        -------
        ModelExecutor
            `ModelExecutor` class instance corresponding to the `model_id`
        """

        try:
            self.add_model_executor(model_id=model_id)  # only adds after checking that is not already added
            return self.find_model_executor_by_id(model_id=model_id)
        except Exception as e:
            logging.error(f"{model_id}: This model could not be added to model_executor list: {e}")
            raise e

    def generate(self, model_id: str, num_samples: int = 30, output_path: str = None, save_images: bool = True,
                 is_gen_function_returned: bool = False, **kwargs):
        """ Generate samples with the model corresponding to the `model_id` or return the model's generate function.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        num_samples: int
            the number of samples that will be generated
        output_path: str
            the path as str to the output folder where the generated samples will be stored
        save_images: bool
            flag indicating whether generated samples are returned (i.e. as list of numpy arrays) or rather stored in file system (i.e in `output_path`)
        is_gen_function_returned: bool
            flag indicating whether, instead of generating samples, the sample generation function will be returned
        **kwargs
            arbitrary number of keyword arguments passed to the model's sample generation function

        Returns
        -------
        list
            Returns images as list of numpy arrays if `save_images` is False. However, if `is_gen_function_returned` is True, it returns the internal generate function of the model.
        """

        model_executor = self.get_model_executor(model_id=model_id)
        return model_executor.generate(num_samples=num_samples, output_path=output_path, save_images=save_images,
                                       is_gen_function_returned=is_gen_function_returned, **kwargs)

    def get_generate_function(self, model_id: str, num_samples: int = 30, output_path: str = None, **kwargs):
        """ Return the model's generate function.

        Relies on the `self.generate` function.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        num_samples: int
            the number of samples that will be generated
        output_path: str
            the path as str to the output folder where the generated samples will be stored
        **kwargs
            arbitrary number of keyword arguments passed to the model's sample generation function

        Returns
        -------
        function
            The internal reusable generate function of the generative model.
        """

        return self.generate(model_id=model_id, num_samples=num_samples, output_path=output_path,
                             is_gen_function_returned=True, **kwargs)

    ############################ OTHER METHODS ############################

    def get_model_as_dataloader(self, model_id: str):
        raise NotImplementedError

    def __repr__(self):
        return f'Generators(model_ids={self.config_manager.model_ids}, model_executors={self.model_executors}, ' \
               f'model_selector: {self.model_selector})'

    def __len__(self):
        return len(self.model_executors)

    def __getitem__(self, idx: int):
        return self.model_executors[idx]
