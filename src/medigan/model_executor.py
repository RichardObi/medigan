# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
@author: Richard Osuala, Noussair Lazrak
BCN-AIM Lab 2021
Contact: richard.osuala@ub.edu
"""

# Import python native libs
from __future__ import absolute_import

import importlib
import time
# Import pypi libs
from pathlib import Path

import pkg_resources

# Import library internal modules
from .constants import CONFIG_FILE_KEY_DEPENDENCIES, CONFIG_FILE_KEY_MODEL_NAME, CONFIG_FILE_KEY_MODEL_EXTENSION, \
    CONFIG_FILE_KEY_PACKAGE_NAME, DEFAULT_OUTPUT_FOLDER, CONFIG_FILE_KEY_PACKAGE_LINK, \
    PACKAGE_EXTENSION, CONFIG_FILE_KEY_IMAGE_SIZE, CONFIG_FILE_KEY_GENERATE, \
    CONFIG_FILE_KEY_GENERATE_NAME, CONFIG_FILE_KEY_GENERATE_ARGS, \
    CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE, CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES, \
    CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH, CONFIG_FILE_KEY_GENERATE_ARGS_CUSTOM, CONFIG_FILE_KEY_GENERATE_ARGS_BASE
from .utils import Utils


class ModelExecutor():
    """ModelExecutor class."""

    def __init__(
            self,
            model_id: str,
            execution_config: object,
            download_package: bool = True,
    ):
        self.model_id = model_id
        self.execution_config = execution_config
        self.download_package = download_package
        self.image_size = None
        self.dependencies = None
        self.model_name = None
        self.model_extension = None
        self.package_name = None
        self.package_link = None
        self.generate_method = None
        self.generate_method_args = None
        self.serialised_model_file_path = None
        self.package_path = None
        self.deserialized_model_as_lib = None
        self._setup_model_package()

    def _setup_model_package(self):
        self.image_size = self.execution_config[CONFIG_FILE_KEY_IMAGE_SIZE]
        self.dependencies = self.execution_config[CONFIG_FILE_KEY_DEPENDENCIES]
        self.model_name = self.execution_config[CONFIG_FILE_KEY_MODEL_NAME]
        self.model_extension = self.execution_config[CONFIG_FILE_KEY_MODEL_EXTENSION]
        self.package_name = self.execution_config[CONFIG_FILE_KEY_PACKAGE_NAME]
        self.package_link = self.execution_config[CONFIG_FILE_KEY_PACKAGE_LINK]
        self.generate_method = self.execution_config[CONFIG_FILE_KEY_GENERATE][
            CONFIG_FILE_KEY_GENERATE_NAME]
        self.generate_method_args = self.execution_config[CONFIG_FILE_KEY_GENERATE][
            CONFIG_FILE_KEY_GENERATE_ARGS]

        self._check_package_resources()
        self._load_package()
        self._import_package_as_lib()

    def _check_package_resources(self):
        print(f"{self.model_id}: Checking availability of dependencies of model: {self.dependencies}")
        try:
            pkg_resources.require(self.dependencies)
            print(f"{self.model_id}: All necessary dependencies for model are available.")
        except Exception as e:
            print(f"{self.model_id}: Some of the necessary dependencies for model are missing: {e}")
            raise e

    def _load_package(self):
        if self.package_path is None:
            assert Utils.mkdirs(
                path_as_string=self.model_id), f"{self.model_id}: The model folder was not found nor created in /{self.model_id}."
            package_path = Path(f"{self.model_id}/{self.package_name}{PACKAGE_EXTENSION}")
            if not Utils.is_file_located_or_downloaded(path_as_string=package_path,
                                                       download_if_not_found=True,
                                                       download_link=self.package_link):
                raise FileNotFoundError(
                    f"{self.model_id}: The package archive ({self.package_name}{PACKAGE_EXTENSION}) was not found in {package_path} nor downloaded from {self.package_link}.")
            self.package_path = package_path

    def _import_package_as_lib(self):
        print(
            f"{self.model_id}: Now importing model package ({self.package_name}) as lib using importlib from {self.package_path}.")
        is_model_already_unpacked = Path(
            f"{self.model_id}/{self.package_name}/{self.model_name}{self.model_extension}").is_file() or Path(
            f"{self.model_id}/{self.model_name}{self.model_extension}").is_file()
        # if is_model_already_unpacked == True, then the package was already unzipped previously.
        if self.package_path.is_file() and PACKAGE_EXTENSION == '.zip' and not is_model_already_unpacked:
            Utils.unzip_archive(source_path=self.package_path, target_path_as_string=self.model_id)
        else:
            print(
                f"{self.model_id}: Either no file found or package already unarchived (not a zip file) in {self.package_path}. No action was taken.")
        try:
            # Installing generative model as python library
            self.deserialized_model_as_lib = importlib.import_module(name=f"{self.model_id}.{self.package_name}")
            self.serialised_model_file_path = f"{self.model_id}/{self.package_name}/{self.model_name}{self.model_extension}"
        except ModuleNotFoundError:
            try:
                # Fallback: The zip's content might have been unzipped in the model_id folder without generating the package_name subfolder.
                self.deserialized_model_as_lib = importlib.import_module(name=f"{self.model_id}")
                self.serialised_model_file_path = f"{self.model_id}/{self.model_name}{self.model_extension}"
            except Exception as e:
                print(f"{self.model_id}: Error while importing {self.package_name} from /{self.model_id}: {e}")
                raise e

    def generate(self, num_samples: int = 20, output_path: str = None, is_gen_function_returned: bool = False,
                 **kwargs):
        if output_path is None:
            output_path = f'{DEFAULT_OUTPUT_FOLDER}/{self.model_id}/{time.time()}/'
            assert Utils.mkdirs(
                path_as_string=output_path), f"{self.model_id}: The output folder was not found nor created in {output_path}."
        try:
            generate_method = getattr(self.deserialized_model_as_lib, f'{self.generate_method}')
            prepared_kwargs = self._prepare_generate_method_args(model_file=self.serialised_model_file_path,
                                                                 num_samples=num_samples, output_path=output_path,
                                                                 **kwargs)
            # return generate_method(self.serialised_model_file_path, self.image_size, num_samples, output_path)
            # print(f"Provided generate function params: {kwargs}")
            # print(f"All generate function params: {prepared_kwargs}")
            if is_gen_function_returned:
                def gen(**some_other_kwargs):
                    generate_method(**prepared_kwargs, **some_other_kwargs)
                return gen
            else:
                generate_method(**prepared_kwargs)
        except Exception as e:
            print(
                f"{self.model_id}: Error while trying to generate images with model {self.serialised_model_file_path}: {e}")
            raise e

    def _prepare_generate_method_args(self, model_file: str, num_samples: int, output_path: str, **kwargs):
        prepared_kwargs: dict = {}
        # get keys of mandatory custom dictionary input args and assign the default value from config to values of keys
        prepared_kwargs.update(self.generate_method_args[CONFIG_FILE_KEY_GENERATE_ARGS_CUSTOM])

        # update: If one of these keys was provided in **kwargs, then change default value to value provided in **kwargs
        prepared_kwargs.update(kwargs)

        try:
            # validating that these specific keys are available in the config. also retrieving default values
            base_config_list = [self.generate_method_args[CONFIG_FILE_KEY_GENERATE_ARGS_BASE][0],
                                self.generate_method_args[CONFIG_FILE_KEY_GENERATE_ARGS_BASE][1],
                                self.generate_method_args[CONFIG_FILE_KEY_GENERATE_ARGS_BASE][2]]
            if not all(x in base_config_list for x in
                       [CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE, CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES,
                        CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH]):
                raise KeyError
        except KeyError as e:
            print(
                f"{self.model_id}: Warning: In this model's config, some required generate method keys ({CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE} "
                f"{CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES} {CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH}) are missing. "
                f" The model's config {self.generate_method_args}: {e}."
                f" A value for this key will be provided nevertheless when calling the model's generate method ({self.generate_method})'. This could cause an error.")
        # Adding the always necessary base parameters to kwargs (updated if these have been erroneously introduced in kwargs)
        prepared_kwargs.update({
            CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE: model_file,
            CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES: num_samples,
            CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH: output_path,
        })
        return prepared_kwargs

    def __repr__(self):
        return f'ModelExecutor(model_id={self.model_id}, name={self.model_name}, package={self.package_name}, ' \
               f'image_size={self.image_size}, dependencies={self.dependencies}, link={self.package_link}, ' \
               f'path={self.serialised_model_file_path}, generate_method={self.generate_method}, ' \
               f'generate_method_args={self.generate_method_args})'

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
