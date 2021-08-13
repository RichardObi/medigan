# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
@author: Richard Osuala, Noussair Lazrak
BCN-AIM Lab 2021
Contact: richard.osuala@ub.edu
"""

# Import python native libs
from __future__ import absolute_import
import pkg_resources
import importlib
import time

# Import pypi libs
from pathlib import Path

# Import library internal modules
from .constants import CONFIG_FILE_KEY_DEPENDENCIES, CONFIG_FILE_KEY_MODEL_NAME, CONFIG_FILE_KEY_MODEL_EXTENSION, \
    CONFIG_FILE_KEY_PACKAGE_NAME, CONFIG_FILE_KEY_GENERATOR, CONFIG_FILE_KEY_GENERATOR_NAME, DEFAULT_OUTPUT_FOLDER, \
    CONFIG_FILE_KEY_PACKAGE_LINK, PACKAGE_EXTENSION, CONFIG_FILE_KEY_IMAGE_SIZE
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
        self.dependencies = None
        self.model_name = None
        self.model_extension = None
        self.package_name = None
        self.package_link = None
        self.generator_function = None
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
        self.generator = self.execution_config[CONFIG_FILE_KEY_GENERATOR]
        self.generator_function = self.execution_config[CONFIG_FILE_KEY_GENERATOR][CONFIG_FILE_KEY_GENERATOR_NAME]
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
        if self.package_path.is_file() and PACKAGE_EXTENSION == '.zip':
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

    def generate(self, number_of_images: int = 20, output_path: str = None):
        if output_path is None:
            output_path = f'{DEFAULT_OUTPUT_FOLDER}/{self.model_id}/{time.time()}/'
            assert Utils.mkdirs(
                path_as_string=output_path), f"{self.model_id}: The output folder was not found nor created in {output_path}."
        try:
            generate_method = getattr(self.deserialized_model_as_lib, f'{self.generator_function}')
            generate_method(self.serialised_model_file_path, self.image_size, number_of_images, output_path)
        except Exception as e:
            print(
                f"{self.model_id}: Error while trying to generate images with model {self.serialised_model_file_path}: {e}")
            raise e

    def get_model_info(self):
        raise NotImplementedError

    def _validate_model_config(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
