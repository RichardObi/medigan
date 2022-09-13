# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" Base class providing user-library interaction methods for config management, and model selection and execution. """

# Import python native libs
from __future__ import absolute_import

import logging

from torch.utils.data import DataLoader, Dataset

# Import library internal modules
from .config_manager import ConfigManager
from .constants import CONFIG_FILE_KEY_EXECUTION, MODEL_ID
from .contribute_model.model_contributor import ModelContributor
from .execute_model.model_executor import ModelExecutor
from .execute_model.synthetic_dataset import SyntheticDataset
from .model_visualizer import ModelVisualizer
from .select_model.model_selector import ModelSelector
from .utils import Utils

# Import pypi libs


class Generators:
    """`Generators` class: Contains medigan's public methods to facilitate users' automated sample generation workflows.

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
        model_contributors: list = None,
        initialize_all_models: bool = False,
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

        if model_contributors is None:
            self.model_contributors = []
        else:
            self.model_contributors = model_contributors

        if initialize_all_models:
            self.add_all_model_executors()

    ############################ CONFIG MANAGER METHODS ############################

    def get_config_by_id(self, model_id: str, config_key: str = None) -> dict:
        """Get and return the part of the config below a `config_key` for a specific `model_id`.

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

        model_id = self.config_manager.match_model_id(provided_model_id=model_id)

        return self.config_manager.get_config_by_id(
            model_id=model_id, config_key=config_key
        )

    def is_model_metadata_valid(
        self, model_id: str, metadata: dict, is_local_model: bool = True
    ) -> bool:
        """Checking if a model's corresponding metadata is valid.

        Specific fields in the model's metadata are mandatory. It is asserted if these key value pairs are present.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        metadata: dict
            The model's corresponding metadata
        is_local_model: bool
            flag indicating whether the tested model is a new local user model i.e not yet part of medigan's official models

        Returns
        -------
        bool
            Flag indicating whether the specific model's metadata format and fields are valid
        """

        return self.config_manager.is_model_metadata_valid(
            model_id=model_id, metadata=metadata, is_local_model=is_local_model
        )

    def add_model_to_config(
        self,
        model_id: str,
        metadata: dict,
        is_local_model: bool = None,
        overwrite_existing_metadata: bool = False,
        store_new_config: bool = True,
    ) -> bool:
        """Adding or updating a model entry in the global metadata.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        metadata: dict
            The model's corresponding metadata
        is_local_model: bool
            flag indicating whether the tested model is a new local user model i.e not yet part of medigan's official models
        overwrite_existing_metadata: bool
            in case of `is_local_model`, flag indicating whether existing metadata for this model in medigan's `config/global.json` should be overwritten.
        store_new_config: bool
            flag indicating whether the current model metadata should be stored on disk i.e. in config/

        Returns
        -------
        bool
            Flag indicating whether model metadata update was successfully concluded
        """

        if is_local_model is None:
            model_id = self.config_manager.match_model_id(provided_model_id=model_id)
            # if no model contributor can be found the model is assumed to be not a local model.
            is_local_model = not is_local_model == self.get_model_contributor_by_id(
                model_id=model_id
            )

        return self.config_manager.add_model_to_config(
            model_id=model_id,
            metadata=metadata,
            is_local_model=is_local_model,
            overwrite_existing_metadata=overwrite_existing_metadata,
            store_new_config=store_new_config,
        )

    ############################ MODEL SELECTOR METHODS ############################

    def list_models(self) -> list:
        """Return the list of model_ids as strings based on config.

        Returns
        -------
        list
        """

        return [model_id for model_id in self.config_manager.model_ids]

    def get_selection_criteria_by_id(
        self, model_id: str, is_model_id_removed: bool = True
    ) -> dict:
        """Get and return the selection config dict for a specific model_id.

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

        model_id = self.config_manager.match_model_id(provided_model_id=model_id)

        return self.model_selector.get_selection_criteria_by_id(model_id=model_id)

    def get_selection_criteria_by_ids(
        self, model_ids: list = None, are_model_ids_removed: bool = True
    ) -> list:
        """Get and return a list of selection config dicts for each of the specified model_ids.

        This function calls an identically named function in a `ModelSelector` instance.

        Parameters
        ----------
        model_ids: list
            A list of generative models' unique ids or ids abbreviated as integers (e.g. 1, 2, .. 21)
        are_model_ids_removed: bool
            flag to remove the model_ids from first level of dictionary.

        Returns
        -------
        list
            a list of dictionaries each corresponding to the selection config of a model
        """

        mapped_model_ids = []
        for model_id in model_ids:
            mapped_model_ids.append(
                self.config_manager.match_model_id(provided_model_id=model_id)
            )

        return self.model_selector.get_selection_criteria_by_ids(
            model_ids=mapped_model_ids, are_model_ids_removed=are_model_ids_removed
        )

    def get_selection_values_for_key(self, key: str, model_id: str = None) -> list:
        """Get and return the value of a specified key of the selection dict in the config for a specific model_id.

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

        return self.model_selector.get_selection_values_for_key(
            key=key, model_id=model_id
        )

    def get_selection_keys(self, model_id: str = None) -> list:
        """Get and return all first level keys from the selection config dict for a specific model_id.

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

    def get_models_by_key_value_pair(
        self, key1: str, value1: str, is_case_sensitive: bool = False
    ) -> list:
        """Get and return a list of model_id dicts that contain the specified key value pair in their selection config.

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

        return self.model_selector.get_models_by_key_value_pair(
            key1=key1, value1=value1, is_case_sensitive=is_case_sensitive
        )

    def rank_models_by_performance(
        self, model_ids: list = None, metric: str = "SSIM", order: str = "asc"
    ) -> list:
        """Rank model based on a provided metric and return sorted list of model dicts.

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

        return self.model_selector.rank_models_by_performance(
            model_ids=model_ids, metric=metric, order=order
        )

    def find_matching_models_by_values(
        self,
        values: list,
        target_values_operator: str = "AND",
        are_keys_also_matched: bool = False,
        is_case_sensitive: bool = False,
    ) -> list:
        """Search for values (and keys) in model configs and return a list of each matching `ModelMatchCandidate`.

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

        return self.model_selector.find_matching_models_by_values(
            values=values,
            target_values_operator=target_values_operator,
            are_keys_also_matched=are_keys_also_matched,
            is_case_sensitive=is_case_sensitive,
        )

    def find_models_and_rank(
        self,
        values: list,
        target_values_operator: str = "AND",
        are_keys_also_matched: bool = False,
        is_case_sensitive: bool = False,
        metric: str = "SSIM",
        order: str = "asc",
    ) -> list:
        """Search for values (and keys) in model configs, rank results and return sorted list of model dicts.

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
        matching_models = self.model_selector.find_matching_models_by_values(
            values=values,
            target_values_operator=target_values_operator,
            are_keys_also_matched=are_keys_also_matched,
            is_case_sensitive=is_case_sensitive,
        )
        if len(matching_models) < 1:
            logging.warning(
                f"For your input, there were {len(matching_models)} matching models, while at least 1 is needed. "
                f"Please adjust either your metric your search value inputs {values} to find at least one match."
            )
        else:
            matching_model_ids = [model.model_id for model in matching_models]
            logging.debug(f"matching_model_ids: {matching_model_ids}")
            ranked_models = self.model_selector.rank_models_by_performance(
                model_ids=matching_model_ids, metric=metric, order=order
            )
            if len(ranked_models) < 1:
                logging.warning(
                    f"None ({len(ranked_models)}) of the {len(matching_model_ids)} found matching models, had a valid metric entry for {metric}. "
                    f"Please adjust your metric to enable ranking of the found models."
                )
        return ranked_models

    def find_models_rank_and_generate(
        self,
        values: list,
        target_values_operator: str = "AND",
        are_keys_also_matched: bool = False,
        is_case_sensitive: bool = False,
        metric: str = "SSIM",
        order: str = "asc",
        num_samples: int = 30,
        output_path: str = None,
        is_gen_function_returned: bool = False,
        install_dependencies: bool = False,
        **kwargs,
    ):
        """Search for values (and keys) in model configs, rank results to generate samples with highest ranked model.

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
        install_dependencies: bool
            flag indicating whether a generative model's dependencies are automatically installed. Else error is raised if missing dependencies are detected.
        **kwargs
            arbitrary number of keyword arguments passed to the model's sample generation function

        Returns
        -------
        None
            However, if `is_gen_function_returned` is True, it returns the internal generate function of the model.
        """
        ranked_models = self.find_models_and_rank(
            values=values,
            target_values_operator=target_values_operator,
            are_keys_also_matched=are_keys_also_matched,
            is_case_sensitive=is_case_sensitive,
            metric=metric,
            order=order,
        )

        assert ranked_models is not None and len(ranked_models) > 0, (
            f"None of the models fulfilled both, the matching (values: {values}) AND "
            f"ranking (metric: {metric}) criteria you provided."
        )

        # Get the ID of the highest ranking model to generate() with that model
        highest_ranking_model_id = ranked_models[0][MODEL_ID]

        # Let's generate with the best-ranked model
        logging.info(
            f"For your input, there were {len(ranked_models)} models found and ranked. "
            f"The highest ranked model ({highest_ranking_model_id}) will now be used for generation: "
            f"{ranked_models[0]}"
        )

        return self.generate(
            model_id=highest_ranking_model_id,
            num_samples=num_samples,
            output_path=output_path,
            is_gen_function_returned=is_gen_function_returned,
            install_dependencies=install_dependencies,
            **kwargs,
        )

    def find_model_and_generate(
        self,
        values: list,
        target_values_operator: str = "AND",
        are_keys_also_matched: bool = False,
        is_case_sensitive: bool = False,
        num_samples: int = 30,
        output_path: str = None,
        is_gen_function_returned: bool = False,
        install_dependencies: bool = False,
        **kwargs,
    ):
        """Search for values (and keys) in model configs to generate samples with the found model.

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
        install_dependencies: bool
            flag indicating whether a generative model's dependencies are automatically installed. Else error is raised if missing dependencies are detected.
        **kwargs
            arbitrary number of keyword arguments passed to the model's sample generation function

        Returns
        -------
        None
            However, if `is_gen_function_returned` is True, it returns the internal generate function of the model.
        """

        matching_models: list = self.model_selector.find_matching_models_by_values(
            values=values,
            target_values_operator=target_values_operator,
            are_keys_also_matched=are_keys_also_matched,
            is_case_sensitive=is_case_sensitive,
        )
        if len(matching_models) > 1:
            logging.error(
                f"For your input, there were more than 1 matching model ({len(matching_models)}). "
                f"Please choose one of the models (see model_ids below) or use find_models_rank_and_generate() instead."
                f"Alternatively, you may also further specify additional search values apart from the provided ones "
                f"to find exactly one model: {values}. The matching models were the following: \n {matching_models}"
            )
        elif len(matching_models) < 1:
            logging.error(
                f"For your input, there were {len(matching_models)} matching models, while 1 is needed. "
                f"Please adjust your search value inputs {values} to find at least one match."
            )
        else:
            # Exactly one matching model. Let's generate with this model
            logging.info(
                f"For your input, there was {len(matching_models)} model matched. "
                f"This model will now be used for generation: {matching_models}"
            )
            matched_model_id = matching_models[0].model_id
            return self.generate(
                model_id=matched_model_id,
                num_samples=num_samples,
                output_path=output_path,
                is_gen_function_returned=is_gen_function_returned,
                install_dependencies=install_dependencies,
                **kwargs,
            )

    ############################ MODEL EXECUTOR METHODS ############################

    def add_all_model_executors(self):
        """Add `ModelExecutor` class instances for all models available in the config.

        Returns
        -------
        None
        """

        for model_id in self.config_manager.model_ids:
            execution_config = self.config_manager.get_config_by_id(
                model_id=model_id, config_key=CONFIG_FILE_KEY_EXECUTION
            )
            self._add_model_executor(
                model_id=model_id, execution_config=execution_config
            )

    def add_model_executor(self, model_id: str, install_dependencies: bool = False):
        """Add one `ModelExecutor` class instance corresponding to the specified `model_id`.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        install_dependencies: bool
            flag indicating whether a generative model's dependencies are automatically installed. Else error is raised if missing dependencies are detected.


        Returns
        -------
        None
        """

        if not self.is_model_executor_already_added(model_id):
            execution_config = self.config_manager.get_config_by_id(
                model_id=model_id, config_key=CONFIG_FILE_KEY_EXECUTION
            )
            self._add_model_executor(
                model_id=model_id,
                execution_config=execution_config,
                install_dependencies=install_dependencies,
            )

    def _add_model_executor(
        self, model_id: str, execution_config: dict, install_dependencies: bool = False
    ):
        """Add one `ModelExecutor` class instance corresponding to the specified `model_id` and `execution_config`.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        execution_config: dict
            The part of the config below the 'execution' key
        install_dependencies: bool
            flag indicating whether a generative model's dependencies are automatically installed. Else error is raised if missing dependencies are detected.

        Returns
        -------
        None
        """

        if not self.is_model_executor_already_added(model_id):
            model_executor = ModelExecutor(
                model_id=model_id,
                execution_config=execution_config,
                download_package=True,
                install_dependencies=install_dependencies,
            )
            self.model_executors.append(model_executor)

    def is_model_executor_already_added(self, model_id) -> bool:
        """Check whether the `ModelExecutor` instance of this model_id is already in `self.model_executors` list.

        Parameters
        ----------
        model_id: str
            The generative model's unique id

        Returns
        -------
        bool
            indicating whether this `ModelExecutor` had been already previously added to `self.model_executors`
        """

        model_id = self.config_manager.match_model_id(provided_model_id=model_id)

        if self.find_model_executor_by_id(model_id=model_id) is None:
            logging.debug(
                f"{model_id}: The model has not yet been added to the model_executor list."
            )
            return False
        return True

    def find_model_executor_by_id(self, model_id: str) -> ModelExecutor:
        """Find and return the `ModelExecutor` instance of this model_id in the `self.model_executors` list.

        Parameters
        ----------
        model_id: str
            The generative model's unique id

        Returns
        -------
        ModelExecutor
            `ModelExecutor` class instance corresponding to the `model_id`
        """

        model_id = self.config_manager.match_model_id(provided_model_id=model_id)

        for idx, model_executor in enumerate(self.model_executors):
            if model_executor.model_id == model_id:
                return model_executor
        return None

    def get_model_executor(
        self, model_id: str, install_dependencies: bool = False
    ) -> ModelExecutor:
        """Add and return the `ModelExecutor` instance of this model_id from the `self.model_executors` list.

        Relies on `self.add_model_executor` and `self.find_model_executor_by_id` functions.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        install_dependencies: bool
            flag indicating whether a generative model's dependencies are automatically installed. Else error is raised if missing dependencies are detected.

        Returns
        -------
        ModelExecutor
            `ModelExecutor` class instance corresponding to the `model_id`
        """

        model_id = self.config_manager.match_model_id(provided_model_id=model_id)

        try:
            self.add_model_executor(
                model_id=model_id,
                install_dependencies=install_dependencies,
            )  # only adds after checking that is not already added
            return self.find_model_executor_by_id(model_id=model_id)
        except Exception as e:
            logging.error(
                f"{model_id}: This model could not be added to model_executor list: {e}"
            )
            raise e

    def generate(
        self,
        model_id: str,
        num_samples: int = 30,
        output_path: str = None,
        save_images: bool = True,
        is_gen_function_returned: bool = False,
        install_dependencies: bool = False,
        **kwargs,
    ):
        """Generate samples with the model corresponding to the `model_id` or return the model's generate function.

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
        install_dependencies: bool
            flag indicating whether a generative model's dependencies are automatically installed. Else error is raised if missing dependencies are detected.
        **kwargs
            arbitrary number of keyword arguments passed to the model's sample generation function

        Returns
        -------
        list
            Returns images as list of numpy arrays if `save_images` is False. However, if `is_gen_function_returned` is True, it returns the internal generate function of the model.
        """

        model_id = self.config_manager.match_model_id(provided_model_id=model_id)

        model_executor = self.get_model_executor(
            model_id=model_id, install_dependencies=install_dependencies
        )
        return model_executor.generate(
            num_samples=num_samples,
            output_path=output_path,
            save_images=save_images,
            is_gen_function_returned=is_gen_function_returned,
            **kwargs,
        )

    def get_generate_function(
        self,
        model_id: str,
        num_samples: int = 30,
        output_path: str = None,
        install_dependencies: bool = False,
        **kwargs,
    ):
        """Return the model's generate function.

        Relies on the `self.generate` function.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        num_samples: int
            the number of samples that will be generated
        output_path: str
            the path as str to the output folder where the generated samples will be stored
        install_dependencies: bool
            flag indicating whether a generative model's dependencies are automatically installed. Else error is raised if missing dependencies are detected.
        **kwargs
            arbitrary number of keyword arguments passed to the model's sample generation function

        Returns
        -------
        function
            The internal reusable generate function of the generative model.
        """

        return self.generate(
            model_id=model_id,
            num_samples=num_samples,
            output_path=output_path,
            is_gen_function_returned=True,
            install_dependencies=install_dependencies,
            **kwargs,
        )

    ############################ MODEL CONTRIBUTOR METHODS ############################

    def add_model_contributor(
        self,
        model_id: str,
        init_py_path: str = None,
    ) -> ModelContributor:
        """Add a `ModelContributor` instance of this model_id to the `self.model_contributors` list.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        init_py_path: str
            The path to the local model's __init__.py file needed for importing and running this model.

        Returns
        -------
        ModelContributor
            `ModelContributor` class instance corresponding to the `model_id`
        """

        model_id = self.config_manager.match_model_id(provided_model_id=model_id)

        model_contributor = self.get_model_contributor_by_id(model_id=model_id)
        if model_contributor is not None:
            logging.warning(
                f"{model_id}: For this model_id, there already exists a ModelContributor. None was added. Returning the existing one."
            )
        else:
            model_contributor = ModelContributor(
                model_id=model_id, init_py_path=init_py_path
            )
            self.model_contributors.append(model_contributor)
        return model_contributor

    def get_model_contributor_by_id(self, model_id: str) -> ModelContributor:
        """Find and return the `ModelContributor` instance of this model_id in the `self.model_contributors` list.

        Parameters
        ----------
        model_id: str
            The generative model's unique id

        Returns
        -------
        ModelContributor
            `ModelContributor` class instance corresponding to the `model_id`
        """

        model_id = self.config_manager.match_model_id(provided_model_id=model_id)

        for idx, model_contributor in enumerate(self.model_contributors):
            if model_contributor.model_id == model_id:
                return model_contributor
        return None

    def add_metadata_from_file(self, model_id: str, metadata_file_path: str) -> dict:
        """Read and parse the metadata of a local model, identified by `model_id`, from a metadata file in json format.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        metadata_file_path: str
            the path pointing to the metadata file

        Returns
        -------
        dict
            Returns a dict containing the contents of parsed metadata json file.
        """

        model_id = self.config_manager.match_model_id(provided_model_id=model_id)

        model_contributor = self.get_model_contributor_by_id(model_id=model_id)
        assert (
            model_contributor is not None
        ), f"{model_id}: No model_contributor is initialized for this model_id in Generators. Add a model_contributor first by running 'add_model_contributor()'."
        return model_contributor.add_metadata_from_file(
            metadata_file_path=metadata_file_path
        )

    def add_metadata_from_input(
        self,
        model_id: str,
        model_weights_name: str,
        model_weights_extension: str,
        generate_method_name: str,
        dependencies: list,
        fill_more_fields_interactively: bool = True,
        output_path: str = "config",
    ) -> dict:
        """Create a metadata dict for a local model, identified by `model_id`, given the necessary minimum metadata contents.

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        model_weights_name: str
            the name of the checkpoint file containing the model's weights
        model_weights_extension: str
            the extension (e.g. .pt) of the checkpoint file containing the model's weights
        generate_method_name: str
            the name of the sample generation method inside the models __init__.py file
        dependencies: list
            the list of dependencies that need to be installed via pip to run the model
        fill_more_fields_interactively: bool
            flag indicating whether a user will be interactively asked via command line for further input to fill out missing metadata content
        output_path: str
            the path where the created metadata json file will be stored

        Returns
        -------
        dict
            Returns a dict containing the contents of the metadata json file.
        """

        model_id = self.config_manager.match_model_id(provided_model_id=model_id)

        model_contributor = self.get_model_contributor_by_id(model_id=model_id)
        assert (
            model_contributor is not None
        ), f"{model_id}: No model_contributor is initialized for this model_id in Generators. Add a model_contributor first by running 'add_model_contributor()'."
        return model_contributor.add_metadata_from_input(
            model_weights_name=model_weights_name,
            model_weights_extension=model_weights_extension,
            generate_method_name=generate_method_name,
            dependencies=dependencies,
            fill_more_fields_interactively=fill_more_fields_interactively,
            output_path=output_path,
        )

    def push_to_zenodo(
        self,
        model_id: str,
        zenodo_access_token: str,
        creator_name: str = "unknown name",
        creator_affiliation: str = "unknown affiliation",
        model_description: str = "",
    ) -> str:
        """Upload the model files as zip archive to a public Zenodo repository where the model will be persistently stored.

        Get your Zenodo access token here: https://zenodo.org/account/settings/applications/tokens/new/ (Enable scopes `deposit:actions` and `deposit:write`)

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        zenodo_access_token: str
            a personal access token in Zenodo linked to a user account for authentication
        creator_name: str
            the creator name that will appear on the corresponding Zenodo model upload homepage
        creator_affiliation: str
            the creator affiliation that will appear on the corresponding Zenodo model upload homepage
        model_description: list
            the model_description that will appear on the corresponding Zenodo model upload homepage

        Returns
        -------
        str
            Returns the url pointing to the corresponding Zenodo model upload homepage
        """
        model_id = self.config_manager.match_model_id(provided_model_id=model_id)

        model_contributor = self.get_model_contributor_by_id(model_id=model_id)
        assert (
            model_contributor is not None
        ), f"{model_id}: No model_contributor is initialized for this model_id in Generators. Add a model_contributor first by running 'add_model_contributor()'."

        return model_contributor.push_to_zenodo(
            access_token=zenodo_access_token,
            creator_name=creator_name,
            creator_affiliation=creator_affiliation,
            model_description=model_description,
        )

    def push_to_github(
        self,
        model_id: str,
        github_access_token: str,
        package_link: str = None,
        creator_name: str = "",
        creator_affiliation: str = "",
        model_description: str = "",
    ):
        """Upload the model's metadata inside a github issue to the medigan github repository.

        To add your model to medigan, your metadata will be reviewed on Github and added to medigan's official model metadata

        The medigan repository issues page: https://github.com/RichardObi/medigan/issues

        Get your Github access token here: https://github.com/settings/tokens

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        github_access_token: str
            a personal access token linked to your github user account, used as means of authentication
        package_link:
            a package link
        creator_name: str
            the creator name that will appear on the corresponding github issue
        creator_affiliation: str
            the creator affiliation that will appear on the corresponding github issue
        model_description: list
            the model_description that will appear on the corresponding github issue

        Returns
        -------
        str
            Returns the url pointing to the corresponding issue on github
        """

        model_id = self.config_manager.match_model_id(provided_model_id=model_id)

        model_contributor = self.get_model_contributor_by_id(model_id=model_id)
        assert (
            model_contributor is not None
        ), f"{model_id}: No model_contributor is initialized for this model_id in Generators. Add a model_contributor first by running 'add_model_contributor()'."

        return model_contributor.push_to_github(
            access_token=github_access_token,
            package_link=package_link,
            creator_name=creator_name,
            creator_affiliation=creator_affiliation,
            model_description=model_description,
        )

    def test_model(
        self,
        model_id: str,
        is_local_model: bool = True,
        overwrite_existing_metadata: bool = False,
        store_new_config: bool = True,
        num_samples: int = 3,
        install_dependencies: bool = False,
    ):
        """Test if a model generates and returns a specific number of samples in the correct format

        Parameters
        ----------
        model_id: str
            The generative model's unique id
        is_local_model: bool
            flag indicating whether the tested model is a new local user model i.e not yet part of medigan's official models
        overwrite_existing_metadata: bool
            in case of `is_local_model`, flag indicating whether existing metadata for this model in medigan's `config/global.json` should be overwritten.
        store_new_config: bool
            flag indicating whether the current model metadata should be stored on disk i.e. in config/
        num_samples: int
            the number of samples that will be generated
        install_dependencies: bool
            flag indicating whether a generative model's dependencies are automatically installed.
            Else error is raised if missing dependencies are detected.
        """

        model_id = self.config_manager.match_model_id(provided_model_id=model_id)

        if is_local_model:
            model_contributor = self.get_model_contributor_by_id(model_id=model_id)

            assert model_contributor is not None, (
                f"{model_id}: No model_contributor is initialized for this model_id. Try to set 'is_local_model=False'"
                f"or add a model_contributor first by running 'add_model_contributor(model_id, init_py_path)' ."
            )

            self.add_model_to_config(
                model_id=model_id,
                metadata=model_contributor.metadata,
                is_local_model=is_local_model,
                overwrite_existing_metadata=overwrite_existing_metadata,
                store_new_config=store_new_config,
            )
        samples = self.generate(
            model_id=model_id,
            save_images=False,
            install_dependencies=install_dependencies,
            num_samples=num_samples,
        )
        assert (
            samples is not None
            and isinstance(samples, list)
            and (
                (len(samples) == num_samples) or (len(samples) > num_samples)
            )  # e.g., len(samples) = num_samples + 1, as sample generation can be restricted to be balanced among classes
        ), (
            f"{model_id}: Model test was not successful. The generated samples {'is None, but ' if samples is None else ''}"
            f"should be a list (actual type: {type(samples)}) and of length {num_samples} (actual length: "
            f"{'None' if samples is None else len(samples)}). Check if input params (e.g. input_path) to model are valid. "
        )  # {f'Generated samples: {samples}' if samples is not None else ''}"

        logging.info(
            f"{model_id}: The test of "
            f"{'this new local user model' if is_local_model else 'this existing medigan model'} "
            f"was successful, as model created the expected number ({num_samples}) of synthetic "
            f"samples."
        )

    def contribute(
        self,
        model_id: str,
        init_py_path: str,
        github_access_token: str,
        zenodo_access_token: str,
        metadata_file_path: str = None,
        model_weights_name: str = None,
        model_weights_extension: str = None,
        generate_method_name: str = None,
        dependencies: list = None,
        fill_more_fields_interactively: bool = True,
        overwrite_existing_metadata: bool = False,
        output_path: str = "config",
        creator_name: str = "unknown name",
        creator_affiliation: str = "unknown affiliation",
        model_description: str = "",
        install_dependencies: bool = False,
    ):
        """Implements the full model contribution workflow including model metadata generation, model test, model Zenodo upload, and medigan github issue creation.

        Parameters
        ----------
        model_id: str
             The generative model's unique id
        init_py_path: str
            The path to the local model's __init__.py file needed for importing and running this model.
        github_access_token: str
            a personal access token linked to your github user account, used as means of authentication
        zenodo_access_token: str
            a personal access token in Zenodo linked to a user account for authentication
        metadata_file_path: str
            the path pointing to the metadata file
        model_weights_name: str
            the name of the checkpoint file containing the model's weights
        model_weights_extension: str
            the extension (e.g. .pt) of the checkpoint file containing the model's weights
        generate_method_name: str
            the name of the sample generation method inside the models __init__.py file
        dependencies: list
            the list of dependencies that need to be installed via pip to run the model
        fill_more_fields_interactively: bool
            flag indicating whether a user will be interactively asked via command line for further input to fill out missing metadata content
        overwrite_existing_metadata: bool
            flag indicating whether existing metadata for this model in medigan's `config/global.json` should be overwritten.
        output_path: str
            the path where the created metadata json file will be stored
        creator_name: str
            the creator name that will appear on the corresponding github issue
        creator_affiliation: str
            the creator affiliation that will appear on the corresponding github issue
        model_description: list
            the model_description that will appear on the corresponding github issue
        install_dependencies: bool
            flag indicating whether a generative model's dependencies are automatically installed.
            Else error is raised if missing dependencies are detected.

        Returns
        -------
        str
            Returns the url pointing to the corresponding issue on github
        """

        # Create model contributor
        self.add_model_contributor(model_id=model_id, init_py_path=init_py_path)

        # Adding the metadata of the model from input
        if metadata_file_path is not None:
            # Using an existing metadata json
            metadata = self.add_metadata_from_file(
                model_id=model_id, metadata_file_path=metadata_file_path
            )
        else:
            # Creating the metadata json
            metadata = self.add_metadata_from_input(
                model_id=model_id,
                model_weights_name=model_weights_name,
                model_weights_extension=model_weights_extension,
                generate_method_name=generate_method_name,
                dependencies=dependencies,
                fill_more_fields_interactively=fill_more_fields_interactively,
                output_path=output_path,
            )
        logging.debug(
            f"{model_id}: The following model metadata was created: {metadata}"
        )

        try:
            self.test_model(
                model_id=model_id,
                is_local_model=True,
                overwrite_existing_metadata=overwrite_existing_metadata,
                install_dependencies=install_dependencies,
            )
        except Exception as e:
            logging.error(
                f"{model_id}: Error while testing this local model. "
                f"Please revise and run model contribute() again. {e}"
            )
            raise e

        # Model Upload to Zenodo
        zenodo_record_url = self.push_to_zenodo(
            model_id=model_id,
            zenodo_access_token=zenodo_access_token,
            creator_name=creator_name,
            creator_affiliation=creator_affiliation,
            model_description=model_description,
        )

        # Creating and returning an issue with model metadata in medigan's Github
        return self.push_to_github(
            model_id=model_id,
            package_link=zenodo_record_url,
            github_access_token=github_access_token,
            creator_name=creator_name,
            creator_affiliation=creator_affiliation,
            model_description=model_description,
        )

    ############################ OTHER METHODS ############################

    def get_as_torch_dataloader(
        self,
        dataset=None,
        model_id: str = None,
        num_samples: int = 1000,
        install_dependencies: bool = False,
        transform=None,
        batch_size=1,
        shuffle=False,
        sampler=None,
        batch_sampler=None,
        num_workers=0,
        collate_fn=None,
        pin_memory=False,
        drop_last=False,
        timeout=0,
        worker_init_fn=None,
        prefetch_factor=2,
        persistent_workers=False,
        **kwargs,
    ) -> DataLoader:

        """Get torch Dataloader sampling synthetic data from medigan model.

        Dataloader combines a dataset and a sampler, and provides an iterable over
        the given torch dataset. Dataloader is created for synthetic data for the specified medigan model.

        Args:
            dataset (Dataset): dataset from which to load the data.
            model_id: str
                The generative model's unique id
            num_samples: int
                the number of samples that will be generated
            install_dependencies: bool
                flag indicating whether a generative model's dependencies are automatically installed.
                Else error is raised if missing dependencies are detected.
            **kwargs
                arbitrary number of keyword arguments passed to the model's sample generation function
                (e.g. the input path for image-to-image translation models in medigan).
            transform
                the torch data transformation functions to be applied to the data in the dataset.
            batch_size (int, optional): how many samples per batch to load
                (default: ``1``).
            shuffle (bool, optional): set to ``True`` to have the data reshuffled
                at every epoch (default: ``False``).
            sampler (Sampler or Iterable, optional): defines the strategy to draw
                samples from the dataset. Can be any ``Iterable`` with ``__len__``
                implemented. If specified, :attr:`shuffle` must not be specified.
            batch_sampler (Sampler or Iterable, optional): like :attr:`sampler`, but
                returns a batch of indices at a time. Mutually exclusive with
                :attr:`batch_size`, :attr:`shuffle`, :attr:`sampler`,
                and :attr:`drop_last`.
            num_workers (int, optional): how many subprocesses to use for data
                loading. ``0`` means that the data will be loaded in the main process.
                (default: ``0``)
            collate_fn (callable, optional): merges a list of samples to form a
                mini-batch of Tensor(s).  Used when using batched loading from a
                map-style dataset.
            pin_memory (bool, optional): If ``True``, the data loader will copy Tensors
                into CUDA pinned memory before returning them.  If your data elements
                are a custom type, or your :attr:`collate_fn` returns a batch that is a custom type,
                see the example below.
            drop_last (bool, optional): set to ``True`` to drop the last incomplete batch,
                if the dataset size is not divisible by the batch size. If ``False`` and
                the size of dataset is not divisible by the batch size, then the last batch
                will be smaller. (default: ``False``)
            timeout (numeric, optional): if positive, the timeout value for collecting a batch
                from workers. Should always be non-negative. (default: ``0``)
            worker_init_fn (callable, optional): If not ``None``, this will be called on each
                worker subprocess with the worker id (an int in ``[0, num_workers - 1]``) as
                input, after seeding and before data loading. (default: ``None``)
            prefetch_factor (int, optional, keyword-only arg): Number of samples loaded
                in advance by each worker. ``2`` means there will be a total of
                2 * num_workers samples prefetched across all workers. (default: ``2``)
            persistent_workers (bool, optional): If ``True``, the data loader will not shutdown
                the worker processes after a dataset has been consumed once. This allows to
                maintain the workers `Dataset` instances alive. (default: ``False``)

        Returns
        -------
        DataLoader
            a torch.utils.data.DataLoader object with data generated by model corresponding to inputted `Dataset` or `model_id`.
        """

        dataset = (
            self.get_as_torch_dataset(
                model_id=model_id,
                num_samples=num_samples,
                install_dependencies=install_dependencies,
                transform=transform,
                **kwargs,
            )
            if dataset is None
            else dataset
        )

        dataloader = DataLoader(
            dataset=dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            sampler=sampler,
            batch_sampler=batch_sampler,
            num_workers=num_workers,
            collate_fn=collate_fn,
            pin_memory=pin_memory,
            drop_last=drop_last,
            timeout=timeout,
            worker_init_fn=worker_init_fn,
            prefetch_factor=prefetch_factor,
            persistent_workers=persistent_workers,
        )

        return dataloader

    def get_as_torch_dataset(
        self,
        model_id: str,
        num_samples: int = 100,
        install_dependencies: bool = False,
        transform=None,
        **kwargs,
    ) -> Dataset:
        """Get synthetic data in a torch Dataset for specified medigan model.

        The dataset returns a dict with keys sample (== image), labels (== condition), and mask (== segmentation mask).
        While key 'sample' is mandatory, the other key value pairs are only returned if applicable to generative model.

        Args:
           model_id: str
               The generative model's unique id
           num_samples: int
               the number of samples that will be generated
           install_dependencies: bool
               flag indicating whether a generative model's dependencies are automatically installed. Else error is raised if missing dependencies are detected.
            transform
                the torch data transformation functions to be applied to the data in the dataset.
           **kwargs
               arbitrary number of keyword arguments passed to the model's sample generation function (e.g. the input path for image-to-image translation models in medigan).

        Returns
        -------
        Dataset
            a torch.utils.data.Dataset object with data generated by model corresponding to `model_id`.
        """

        data = self.generate(
            model_id=model_id,
            num_samples=num_samples,
            is_gen_function_returned=False,
            install_dependencies=install_dependencies,
            save_images=False,  # design decision: temporary storage in memory instead of I/O from disk
            **kwargs,
        )

        logging.debug(f"data: {data}")

        (
            samples,
            masks,
            other_imaging_output,
            labels,
        ) = Utils.split_images_masks_and_labels(data=data, num_samples=num_samples)
        logging.debug(
            f"samples: {samples} \n masks: {masks} \n other_imaging_output: {other_imaging_output} \n labels: {labels}"
        )

        return SyntheticDataset(
            samples=samples,
            masks=masks,
            other_imaging_output=other_imaging_output,
            labels=labels,
            transform=transform,
        )

    def visualize(
        self,
        model_id: str,
        slider_grouper: int = 10,
        auto_close: bool = False,
        install_dependencies: bool = False,
    ) -> None:
        """Initialize and run `ModelVisualizer` of this model_id if it is available.
        It allows to visualize a sample from the model's output.
        UI window will pop up allowing the user to control the generation parameters (conditional and unconditional ones).

        Parameters
        ----------
        model_id: str
            The generative model's unique id to visualize.
        slider_grouper: int
            Number of input parameters to group together within one slider.
        auto_close: bool
            Flag for closing the user interface automatically after time. Used while testing.
        install_dependencies: bool
            flag indicating whether a generative model's dependencies are automatically installed. Else error is raised if missing dependencies are detected.

        """

        model_id = self.config_manager.match_model_id(provided_model_id=model_id)

        config = self.get_config_by_id(model_id=model_id)
        model_executor = self.get_model_executor(
            model_id=model_id, install_dependencies=install_dependencies
        )

        ModelVisualizer(model_executor=model_executor, config=config).visualize(
            slider_grouper=slider_grouper, auto_close=auto_close
        )

    def __repr__(self):
        return (
            f"Generators(model_ids={self.config_manager.model_ids}, model_executors={self.model_executors}, "
            f"model_selector: {self.model_selector})"
        )

    def __len__(self):
        return len(self.model_executors)

    def __getitem__(self, idx: int):
        return self.model_executors[idx]
