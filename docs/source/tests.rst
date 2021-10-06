Tests
==============

.. contents:: Table of Contents

To facilitate testing if `medigan` is setup correctly and whether all of the features in `medigan` work as desired, the following set of automated test cases is provided.
Below each test procedure is described and a command is provided to run each test.

Setup medigan for running tests
_______________________________________
Open your command line, and clone `medigan` from Github with:

.. code-block:: Python

    git clone https://github.com/RichardObi/medigan.git
    cd medigan

To install dependencies and to setup and activate a virtual environment, run:

.. code-block:: Python

    pip install pipenv
    pipenv install
    pipenv shell


Test 1: test_medigan_imports
_______________________________________
This test checks if `medigan` can be imported correctly.

.. code-block:: Python

    python -m tests.tests TestMediganMethods.test_medigan_imports

Test 2: test_init_generators
_______________________________________
This test checks if the central `generators` class can be initialised correctly.

.. code-block:: Python

    python -m tests.tests TestMediganMethods.test_init_generators


Test 3: test_generate_methods
_______________________________________
This test examines whether samples can be created with any of three example generative models (`1 <https://doi.org/10.5281/zenodo.5187714>`_, `2 <https://doi.org/10.5281/zenodo.5188557>`_, `3 <https://doi.org/10.5281/zenodo.5547263>`_) in `medigan`.

.. code-block:: Python

    python -m tests.tests TestMediganMethods.test_generate_methods


Test 4: test_generate_methods_with_additional_args
______________________________________________________
Additional key-value pair arguments (kwargs) can be provided to the `generate()` method of a generative model.
This test checks if these additional arguments are passed correctly to the generate method and whether the generate method's returned result corresponds to the passed arguments.

.. code-block:: Python

    python -m tests.tests TestMediganMethods.test_generate_methods_with_additional_args


Test 5: test_get_generate_method
______________________________________________________
The `generate()` method of any of the generative models in `medigan` can be returned.
This makes it easier to integrate the `generate()` function dynamically into users' data processing and training pipelines i.e. avoiding it to reload the model weights each time it is called.
This test tests if the `generate()` method is successfully returned and usable thereafter.

.. code-block:: Python

    python -m tests.tests TestMediganMethods.test_get_generate_method


Test 6: test_search_for_models_method
______________________________________________________
The tested function searches for a model by matching provided key words with the information in the model's `config <https://github.com/RichardObi/medigan-models>`_.
This test checks whether the expected models are found accordingly.

.. code-block:: Python

    python -m tests.tests TestMediganMethods.test_search_for_models_method


Test 7: test_find_model_and_generate_method
______________________________________________________
After searching and finding one specific model, the tested function generates samples with that model.
This test checks whether the expected model is found and whether samples are generated accordingly.

.. code-block:: Python

    python -m tests.tests TestMediganMethods.test_find_model_and_generate_method


Test 8: test_rank_models_by_performance
______________________________________________________
Provided a list of model ids, the tested function rankes these models by a performance metric.
The performance metrics are stored in the models' `config <https://github.com/RichardObi/medigan-models>`_.
This test checks whether the ranking worked and whether the expected model is ranked the highest.

.. code-block:: Python

    python -m tests.tests TestMediganMethods.test_rank_models_by_performance


Test 9: test_find_and_rank_models_by_performance
______________________________________________________
After searching and finding various models, the tested function ranks these models by a performance metric.
This test checks whether the expected model is found, and whether it is the highest ranked one and whether it generated samples accordingly.

.. code-block:: Python

    python -m tests.tests TestMediganMethods.test_find_and_rank_models_by_performance


Test 10: test_find_and_rank_models_then_generate_method
_____________________________________________________________________
After searching and finding various models, the tested function ranks these models by a performance metric and generates samples with the highest ranked model.
This test checks whether the expected model is found, whether it is the highest ranked one and whether it generated samples accordingly.

.. code-block:: Python

    python -m tests.tests TestMediganMethods.test_find_and_rank_models_then_generate_method


Test 11: test_get_models_by_key_value_pair
______________________________________________________
After receiving a key value pair, the tested function returns all models that have that key-value pair in their model `config <https://github.com/RichardObi/medigan-models>`_.
This test checks whether the expected models are found and returned correctly.

.. code-block:: Python

    python -m tests.tests TestMediganMethods.test_get_models_by_key_value_pair


