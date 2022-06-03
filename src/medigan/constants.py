# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""Global constants of the medigan library

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
.. codeauthor:: Noussair Lazrak <lazrak.noussair@gmail.com>
"""

""" Static link to the config of medigan. Note: To add a model, please create pull request in this github repo. """
CONFIG_FILE_URL = (
    "https://raw.githubusercontent.com/RichardObi/medigan/main/config/global.json"
)

""" Folder path that will be created to locally store the config file. """
CONFIG_FILE_FOLDER = "config"

""" Name and extensions of config file. """
CONFIG_FILE_NAME_AND_EXTENSION = "global.json"

""" The key under which the execution dictionary of a model is nested in the config file. """
CONFIG_FILE_KEY_EXECUTION = "execution"

""" The key under which the selection dictionary of a model is nested in the config file. """
CONFIG_FILE_KEY_SELECTION = "selection"

""" The key under which the description dictionary of a model is nested in the config file. """
CONFIG_FILE_KEY_DESCRIPTION = "description"

""" Below the selection dict, the key under which the performance dictionary of a model is nested in the config file. """
CONFIG_FILE_KEY_PERFORMANCE = "performance"

""" Below the execution dict, the key under which the dependencies dictionary of a model is nested in the config file. """
CONFIG_FILE_KEY_DEPENDENCIES = "dependencies"

""" Below the execution dict, the key under which the package link of a model is present in the config file. 
Note: The model packages are per convention stored on Zenodo where they retrieve a static DOI avoiding security issues 
due to static non-modifiable content on Zenodo. Zenodo also helps to maintain clarity of who the owners and contributors
of each generative model (and its IP) in medigan are. """
CONFIG_FILE_KEY_PACKAGE_LINK = "package_link"

""" Below the execution dict, the key under which the extension of a model is present in the config file. """
CONFIG_FILE_KEY_MODEL_EXTENSION = "extension"

""" Below the execution dict, the key under which the package_name of a model is present in the config file. """
CONFIG_FILE_KEY_PACKAGE_NAME = "package_name"

""" Below the execution dict, the key under which the package_name of a model is present in the config file. """
CONFIG_FILE_KEY_GENERATOR = "generator"

""" Below the execution dict, the key under which a model's generator's is present in the config file. """
CONFIG_FILE_KEY_GENERATOR_NAME = "name"

""" Below the execution dict, the key under which a model's image_size is present in the config file. """
CONFIG_FILE_KEY_IMAGE_SIZE = "image_size"

""" Below the execution dict, the key under which a model's name is present in the config file. """
CONFIG_FILE_KEY_MODEL_NAME = "model_weights_name"

""" Below the execution dict, the key under which a nested dict with info on the model's generate() function is present. """
CONFIG_FILE_KEY_GENERATE = "generate_method"

""" Below the execution dict, the key under which the exact name of a model's generate() function is present. """
CONFIG_FILE_KEY_GENERATE_NAME = "name"

""" Below the execution dict, the key under which a nested dict with info on the arguments of a model's generate() function is present. """
CONFIG_FILE_KEY_GENERATE_ARGS = "args"

""" Below the execution dict, the key under which an array of mandatory base arguments of any model's generate() function is present. """
CONFIG_FILE_KEY_GENERATE_ARGS_BASE = "base"

""" Below the execution dict, the key under which a nested dict of key-value pairs of model specific custom arguments of a model's generate() function are present. """
CONFIG_FILE_KEY_GENERATE_ARGS_CUSTOM = "custom"

""" Below the execution dict, the key under which the model_file argument value of any model's generate() function is present. """
CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE = "model_file"

""" Below the execution dict, the key under which the num_samples argument value of any model's generate() function is present. """
CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES = "num_samples"

""" Below the execution dict, the key under which the output_path argument value of any model's generate() function is present. """
CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH = "output_path"

""" Below the execution dict, the key under which the save images boolean flag argument value of any model's generate() function is present. """
CONFIG_FILE_KEY_GENERATE_ARGS_SAVE_IMAGES = "save_images"

""" Below the selectoin dict, the key under which the tags (list of strings) is present. """
CONFIG_FILE_KEY_TAGS = "tags"

""" The filetype of any of the generative model's python packages after download and before unpacking. """
PACKAGE_EXTENSION = ".zip"

""" The string describing a model's unique id in medigan's data structures. """
MODEL_ID = "model_id"

""" The default path to a folder under which the outputs of the medigan package (i.e. generated samples) are stored. """
DEFAULT_OUTPUT_FOLDER = "output"

""" The folder containing an __init__.py file is a python module. """
INIT_PY_FILE = "__init__.py"

""" Name and extensions of template of config file. """
CONFIG_TEMPLATE_FILE_NAME_AND_EXTENSION = "template.json"

""" Name and extensions of template of config file. """
TEMPLATE_FOLDER = "templates"

""" A generic description appended to model uploads that are automatically uploaded to zenodo via Zenodo API call in medigan"""
ZENODO_GENERIC_MODEL_DESCRIPTION = "\n This generative model is used as part of the medigan library. \n medigan is an open-source Python library on Github that allows developers and researchers to easily add synthetic imaging data into their model training pipelines. \n medigan github repository: https://github.com/RichardObi/medigan \n Please find the medigan documentation here: https://medigan.readthedocs.io/"
