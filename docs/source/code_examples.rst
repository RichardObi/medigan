Code Examples
==============

.. contents:: Table of Contents

Install
__________________________
Install `medigan` library from pypi (or github).

.. code-block:: Python

    pip install medigan

Import `medigan` and initialize Generators

.. code-block:: Python

    from medigan import Generators
    generators = Generators()


Generate Images
_______________________________________
Generate 10 samples using one (model 1 is `00001_DCGAN_MMG_CALC_ROI`) of the `medigan models <https://doi.org/10.5281/zenodo.5187714>`_ from the `config <https://github.com/RichardObi/medigan-models/blob/main/global.json>`_.

`install_dependencies` signals to medigan that the user wishes to automatically install all the python dependencies (e.g. numpy. torch, etc) required to run this model (i.e. to the user's active python environment).

.. code-block:: Python

    generators.generate(model_id=1, num_samples=10, install_dependencies=True)

Get the model's generate method and run it to generate 3 samples

.. code-block:: Python

    # model 1 is "00001_DCGAN_MMG_CALC_ROI"
    gen_function = generators.get_generate_function(model_id=1, num_samples=3)
    gen_function()

Get the model's synthetic data as torch dataloader with 3 samples

.. code-block:: Python

    # model 4 is "00004_PIX2PIX_MMG_MASSES_W_MASKS"
    dataloader = generators.get_as_torch_dataloader(model_id=4, num_samples=3)


Visualize Generative Model
_______________________________________

Displays an interactive visual interface for exploration of applicable models.

.. code-block:: Python

    # model 10 is "00010_FASTGAN_POLYP_PATCHES_W_MASKS"
    generators.visualize(10)

.. figure:: _static/interface.png
   :alt: Visualization example for model 00010

Search for Generative Models
_______________________________________
Find all models that contain a specific key-value pair in their model config.

.. code-block:: Python

    key = "modality"
    value = "Full-Field Mammography"
    found_models = generators.get_models_by_key_value_pair(key1=key, value1=value, is_case_sensitive=False)
    print(found_models)

Create a list of search terms and find the models that have these terms in their config.

.. code-block:: Python

    values_list = ['dcgan', 'Mammography', 'inbreast']
    models = generators.find_matching_models_by_values(values=values_list, target_values_operator='AND', are_keys_also_matched=True, is_case_sensitive=False)
    print(f'Found models: {models}')

Create a list of search terms, find a model and generate

.. code-block:: Python

    values_list = ['dcgan', 'mMg', 'ClF', 'modalities', 'inbreast']
    generators.find_model_and_generate(values=values_list, target_values_operator='AND', are_keys_also_matched=True, is_case_sensitive=False, num_samples=5)

Rank Generative Models
_______________________________________
Rank the models by a performance metric and return ranked list of models

.. code-block:: Python

    ranked_models = generators.rank_models_by_performance(metric="SSIM", order="asc")
    print(ranked_models)

Find the models, then rank them by a performance metric and return ranked list of models

.. code-block:: Python

    ranked_models = generators.find_models_and_rank(values=values_list, target_values_operator='AND', are_keys_also_matched=True, is_case_sensitive=False, metric="SSIM", order="asc")
    print(ranked_models)

Find the models, then rank them, and then generate samples with the best ranked model.

.. code-block:: Python

    generators.find_models_rank_and_generate(values=values_list, target_values_operator='AND', are_keys_also_matched=True, is_case_sensitive=False, metric="SSIM", order="asc", num_samples=5)
