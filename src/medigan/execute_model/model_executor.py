# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""Model executor class that downloads models, loads them as python packages, and runs their generate functions. """

# Import python native libs
from __future__ import absolute_import

import importlib
import logging
import os
import time

# Import pypi libs
from pathlib import Path

import pkg_resources
from tqdm import tqdm

# Import library internal modules
from ..constants import (
    CONFIG_FILE_KEY_DEPENDENCIES,
    CONFIG_FILE_KEY_GENERATE,
    CONFIG_FILE_KEY_GENERATE_ARGS,
    CONFIG_FILE_KEY_GENERATE_ARGS_BASE,
    CONFIG_FILE_KEY_GENERATE_ARGS_CUSTOM,
    CONFIG_FILE_KEY_GENERATE_ARGS_INPUT_LATENT_VECTOR_SIZE,
    CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE,
    CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES,
    CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH,
    CONFIG_FILE_KEY_GENERATE_ARGS_SAVE_IMAGES,
    CONFIG_FILE_KEY_GENERATE_NAME,
    CONFIG_FILE_KEY_IMAGE_SIZE,
    CONFIG_FILE_KEY_MODEL_EXTENSION,
    CONFIG_FILE_KEY_MODEL_NAME,
    CONFIG_FILE_KEY_PACKAGE_LINK,
    CONFIG_FILE_KEY_PACKAGE_NAME,
    DEFAULT_OUTPUT_FOLDER,
    MODEL_FOLDER,
    PACKAGE_EXTENSION,
)
from ..utils import Utils
from .install_model_dependencies import install_model


class ModelExecutor:
    """`ModelExecutor` class: Find config links to download models, init models as python packages, run generate methods.

    Parameters
    ----------
    model_id: str
        The generative model's unique id
    execution_config: dict
        The part of the config below the 'execution' key
    download_package: bool
        Flag indicating, if True, that the model's package should be downloaded instead of using an existing one that
        was downloaded previously
    install_dependencies: bool
            flag indicating whether a generative model's dependencies are automatically installed. Else error is raised if missing dependencies are detected.


    Attributes
    ----------
    model_id: str
        The generative model's unique id
    execution_config: dict
        The part of the config below the 'execution' key
    download_package: bool
        Flag indicating, if True, that the model's package should be downloaded instead of using an existing one that
        was downloaded previously
    image_size: int
        Pixel dimension of the generated samples, where images are assumed to have the same width and height
    dependencies: list
        List of the dependencies of a models python package.
    model_name: str
        Name of the generative model
    model_extension: str
        File extension of the generative model's weights file.
    package_name: str
        Name of the model's python package i.e. the name of the model's zip file and unzipped package folder
    package_link: str
        The link to the zipped model package. Note: Convention is to host models on Zenodo (reason: static doi content)
    generate_method_name: str
        The name of the model's generate method inside the model package. This method is called to generate samples.
    generate_method_args: dict
        The args of the model's generate method inside the model package
    serialised_model_file_path: str
        Path as string to the generative model's weights file
    package_path: str
        Path as string to the generative model's python package containing an `__init__.py` file
    deserialized_model_as_lib
        The generative model's package imported as python library. Generate method inside this library can be called.
    """

    def __init__(
        self,
        model_id: str,
        execution_config: dict,
        download_package: bool = True,
        install_dependencies: bool = False,
    ):
        self.model_id = model_id
        self.execution_config = execution_config
        self.download_package = download_package
        self.install_dependencies = install_dependencies
        self.image_size = None
        self.dependencies = None
        self.model_name = None
        self.model_extension = None
        self.package_name = None
        self.package_link = None
        self.generate_method_name = None
        self.generate_method_args = None
        self.generate_method_input_latent_vector_size = None
        self.serialised_model_file_path = None
        self.package_path = None
        self.deserialized_model_as_lib = None
        self._setup_model_package()

    def _setup_model_package(self):
        """Use specific keys to retrieve needed model config values and load and initialize the model as package."""

        self.image_size = self.execution_config[CONFIG_FILE_KEY_IMAGE_SIZE]
        self.dependencies = self.execution_config[CONFIG_FILE_KEY_DEPENDENCIES]
        self.model_name = self.execution_config[CONFIG_FILE_KEY_MODEL_NAME]
        self.model_extension = self.execution_config[CONFIG_FILE_KEY_MODEL_EXTENSION]
        self.package_name = self.execution_config[CONFIG_FILE_KEY_PACKAGE_NAME]
        self.package_link = self.execution_config[CONFIG_FILE_KEY_PACKAGE_LINK]
        self.generate_method_name = self.execution_config[CONFIG_FILE_KEY_GENERATE][
            CONFIG_FILE_KEY_GENERATE_NAME
        ]
        self.generate_method_args = self.execution_config[CONFIG_FILE_KEY_GENERATE][
            CONFIG_FILE_KEY_GENERATE_ARGS
        ]
        if (
            CONFIG_FILE_KEY_GENERATE_ARGS_INPUT_LATENT_VECTOR_SIZE
            in self.execution_config[CONFIG_FILE_KEY_GENERATE]
        ):
            self.generate_method_input_latent_vector_size = self.execution_config[
                CONFIG_FILE_KEY_GENERATE
            ][CONFIG_FILE_KEY_GENERATE_ARGS_INPUT_LATENT_VECTOR_SIZE]

        self._check_package_resources()
        if not self.is_model_already_unpacked():
            self._get_and_store_package()
        self._import_package_as_lib()

    def _check_package_resources(self):
        """Check if the dependencies inside the generative model's package are installed in the current setup."""

        logging.debug(
            f"{self.model_id}: Now checking availability of dependencies of model: {self.dependencies}"
        )
        try:
            pkg_resources.require(self.dependencies)
            logging.debug(
                f"{self.model_id}: All necessary dependencies for model are available: {self.dependencies}"
            )
        except Exception as e:
            if self.install_dependencies:
                logging.info(
                    f"{self.model_id}: Now installing dependencies using pip for model {self.dependencies}. This may take a few minutes."
                )
                install_model(
                    model_id=self.model_id, execution_config=self.execution_config
                )
            else:
                raise Exception(
                    f"{self.model_id}: Some of the necessary dependencies ({self.dependencies}) for this model "
                    f"are missing. Either set install_dependencies=True or manually run 'python src/medigan/install_model_dependencies.py --model_id {self.model_id}' to install them. Error: {e}"
                )

    def _get_and_store_package(self):
        """Load and store the generative model's python package using the link from the model's `execution_config`."""

        if self.package_path is None:
            assert Utils.mkdirs(path_as_string=f"{MODEL_FOLDER}/{self.model_id}"), (
                f"{self.model_id}: The model folder was not found nor created "
                f"in {MODEL_FOLDER}/{self.model_id}."
            )
            package_path = Path(
                f"{MODEL_FOLDER}/{self.model_id}/{self.package_name}{PACKAGE_EXTENSION}"
            )
            try:
                if not Utils.is_file_located_or_downloaded(
                    path_as_string=package_path,
                    download_if_not_found=True,
                    download_link=self.package_link,
                ):
                    error_string = (
                        f"{self.model_id}: The package archive ({self.package_name}{PACKAGE_EXTENSION}) "
                        f"was not found in {package_path} nor downloaded from {self.package_link}."
                    )
                    raise FileNotFoundError(error_string)
            except Exception as e:
                raise e
            self.package_path = package_path
        logging.info(
            f"{self.model_id}: Model package should now be available in: {self.package_path}."
        )

    def is_model_already_unpacked(self) -> bool:
        """Check if a valid path to the model files exists and, if so, set the `package_path`"""

        path_option_1 = Path(
            f"{MODEL_FOLDER}/{self.model_id}/{self.package_name}/{self.model_name}{self.model_extension}"
        )

        path_option_2 = Path(
            f"{MODEL_FOLDER}/{self.model_id}/{self.model_name}{self.model_extension}"
        )

        if path_option_1.is_file():
            self.package_path = path_option_1
            return True

        if path_option_2.is_file():
            self.package_path = path_option_2
            return True

        return False

    def _import_package_as_lib(self):
        """Unzip and import the generative model's python package using importlib."""

        logging.debug(
            f"{self.model_id}: Now importing model package ({self.package_name}) as lib using "
            f"importlib from {self.package_path}."
        )
        is_model_already_unpacked = self.is_model_already_unpacked()
        # if is_model_already_unpacked == True, then the package was already unzipped previously.

        if (
            self.package_path.is_file()
            and PACKAGE_EXTENSION == ".zip"
            and not is_model_already_unpacked
        ):
            # Unzip the model package in {MODEL_FOLDER}/{model_id}/{MODEL_PACKAGE}{PACKAGE_EXTENSION}
            Utils.unzip_archive(
                source_path=self.package_path,
                target_path=f"{MODEL_FOLDER}/{self.model_id}",
            )
        else:
            logging.debug(
                f"{self.model_id}: Either no file found (== {self.package_path.is_file()}) or package "
                f"already unarchived (=={is_model_already_unpacked}) in {self.package_path}. "
                f"No action was taken."
            )
        try:
            # Installing generative model as python library
            self.deserialized_model_as_lib = importlib.import_module(
                name=f"{MODEL_FOLDER}.{self.model_id}.{self.package_name}"
            )
            if not hasattr(
                self.deserialized_model_as_lib, f"{self.generate_method_name}"
            ):
                # if generate method is not in lib path, generating samples will not work. Next: Check fallback folder.
                raise ModuleNotFoundError
            self.serialised_model_file_path = f"{MODEL_FOLDER}/{self.model_id}/{self.package_name}/{self.model_name}{self.model_extension}"
        except ModuleNotFoundError:
            try:
                # Fallback: The zip's content might have been unzipped in the model_id folder without generating the package_name subfolder.
                self.deserialized_model_as_lib = importlib.import_module(
                    name=f"{MODEL_FOLDER}.{self.model_id}"
                )
                if not hasattr(
                    self.deserialized_model_as_lib, f"{self.generate_method_name}"
                ):
                    # if generate method is not in lib path, generating samples will not work. Next: Check fallback folder.
                    raise AttributeError(
                        f"Module '{MODEL_FOLDER}.{self.model_id}' has no attribute "
                        f"'{self.generate_method_name}' (generate method). We also tried module "
                        f"'{MODEL_FOLDER}.{self.model_id}.{self.package_name}'. Please check if "
                        f"generate_method_name and package_name are correct for this model in its "
                        f"global.json entry."
                    )
                self.serialised_model_file_path = f"{MODEL_FOLDER}/{self.model_id}/{self.model_name}{self.model_extension}"
            except Exception as e:
                logging.error(
                    f"{self.model_id}: Error occurred while trying to import "
                    f"'{MODEL_FOLDER}.{self.model_id}.{self.package_name}'."
                    f"Fallback import of '{MODEL_FOLDER}.{self.model_id}' also failed. "
                    f"Please make sure the module '{MODEL_FOLDER}' is not imported from elsewhere in your syspath: {e}"
                )
                raise e

    def generate(
        self,
        num_samples: int = 20,
        output_path: str = None,
        save_images: bool = True,
        is_gen_function_returned: bool = False,
        batch_size: int = 32,
        **kwargs,
    ):
        """Generate samples using the generative model or return the model's generate function.

        The name amd additional parameters of the generate function of the respective generative model are retrieved
        from the model's `execution_config`.

        Parameters
        ----------
        num_samples: int
            the number of samples that will be generated
        output_path: str
            the path as str to the output folder where the generated samples will be stored
        save_images: bool
            flag indicating whether generated samples are returned (i.e. as list of numpy arrays) or rather stored in file system (i.e in `output_path`)
        is_gen_function_returned: bool
            flag indicating whether, instead of generating samples, the sample generation function will be returned
        batch_size: int
            the batch size for the sample generation function
        **kwargs
            arbitrary number of keyword arguments passed to the model's sample generation function

        Returns
        -------
        list
            Returns images as list of numpy arrays if `save_images` is False. However, if `is_gen_function_returned` is True, it returns the internal generate function of the model.

        Raises
        ------
        Exception
            If the generate method of the model does not exist, cannot be called, or is called with missing params, or
            if the sample generation inside the model package returns an exception.
        """

        if output_path is None:
            output_path = f"{DEFAULT_OUTPUT_FOLDER}/{self.model_id}/{time.time()}/"
        assert Utils.mkdirs(
            path_as_string=output_path
        ), f"{self.model_id}: The output folder was not found nor created in {output_path}."
        try:
            generate_method = getattr(
                self.deserialized_model_as_lib, f"{self.generate_method_name}"
            )
            prepared_kwargs = self._prepare_generate_method_args(
                model_file=self.serialised_model_file_path,
                num_samples=num_samples,
                output_path=output_path,
                save_images=save_images,
                **kwargs,
            )
            logging.debug(f"The generate function's parameters are: {prepared_kwargs}")
            if is_gen_function_returned:

                def gen(**some_other_kwargs):
                    logging.debug(
                        f"Generate method called with the following params. (i) default: {prepared_kwargs}, "
                        f"(ii) custom: {some_other_kwargs}"
                    )
                    prepared_kwargs.update(some_other_kwargs)
                    return generate_method(**prepared_kwargs)

                return gen
            elif save_images:
                sample_index = 1
                prepared_kwargs.update({"num_samples": batch_size})
                for batch_num in tqdm(range(0, num_samples // batch_size + 1)):
                    if batch_num == num_samples // batch_size:
                        batch_size = num_samples % batch_size
                        prepared_kwargs.update({"num_samples": batch_size})

                    batch_path = (
                        os.path.join(output_path, "batch_" + str(batch_num)) + "/"
                    )

                    # Generate the path in case it is not yet available.
                    assert Utils.mkdirs(
                        path_as_string=batch_path
                    ), f"{self.model_id}: The batch path was not found nor created in {batch_path}."

                    prepared_kwargs.update({"output_path": batch_path})

                    generate_method(**prepared_kwargs)

                    for filename in os.listdir(batch_path):
                        os.rename(
                            os.path.join(batch_path, filename),
                            os.path.join(
                                output_path, "batch_" + str(batch_num) + "_" + filename
                            ),
                        )
                        sample_index += 1

                    os.rmdir(batch_path)
            else:
                return generate_method(**prepared_kwargs)

        except Exception as e:
            logging.error(
                f"{self.model_id}: Error while trying to generate images with model "
                f"{self.serialised_model_file_path}: {e}"
            )
            raise e

    def _prepare_generate_method_args(
        self,
        model_file: str,
        num_samples: int,
        output_path: str,
        save_images: bool,
        **kwargs,
    ):
        """Prepare the keyword arguments that will be passed to the models generate function.

        Prepares the keyword arguments that need to be passed to the generative model's generate function to generate
        samples. This contains the steps:

            - Update keyword args dict with default values for all params from model config

            - Update keyword args dict with the `**args` provided by user thus overwriting the previously set default
                values for which user has provided key-value pairs.

            - Checking if all mandatory 'base' values are set in model config.

            - Update keyword args dict with 'base' key-value pairs, which i.e. are the param values for `model_file`,
            `num_samples` and `output_path`, thus overwriting any previously set value for these keys.

            - Returning the updated and prepared keyword args dict

        Parameters
        ----------
        model_file : str
            the path to the serialized weights of the generative model.
        num_samples: int
            the number of samples that will be generated
        output_path: str
            the path as str to the output folder where the generated samples will be stored
        **kwargs
            arbitrary number of keyword arguments passed to the model's sample generation function

        Returns
        -------
        dict
            kwargs as dictionary containing both user input params (prioritized) and config input params of the model
        """

        prepared_kwargs: dict = {}
        # get keys of mandatory custom dictionary input args and assign the default value from config to values of keys
        prepared_kwargs.update(
            self.generate_method_args[CONFIG_FILE_KEY_GENERATE_ARGS_CUSTOM]
        )

        # update: If one of these keys was provided in **kwargs, then change default value to value provided in **kwargs
        prepared_kwargs.update(kwargs)

        try:
            # validating that these specific keys are available in the config. also retrieving default values
            base_config_list = [
                self.generate_method_args[CONFIG_FILE_KEY_GENERATE_ARGS_BASE][0],
                self.generate_method_args[CONFIG_FILE_KEY_GENERATE_ARGS_BASE][1],
                self.generate_method_args[CONFIG_FILE_KEY_GENERATE_ARGS_BASE][2],
                self.generate_method_args[CONFIG_FILE_KEY_GENERATE_ARGS_BASE][3],
            ]
            if not all(
                x in base_config_list
                for x in [
                    CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE,
                    CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES,
                    CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH,
                    CONFIG_FILE_KEY_GENERATE_ARGS_SAVE_IMAGES,
                ]
            ):
                raise KeyError
        except KeyError as e:
            logging.warning(
                f"{self.model_id}: Warning: In this model's generate args ({self.generate_method_args}), some "
                f"required generate method keys ({CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE}, "
                f"{CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES}, {CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH}, "
                f"{CONFIG_FILE_KEY_GENERATE_ARGS_SAVE_IMAGES}) are missing: {e}. A value for this key will be "
                f"provided nevertheless when calling the model's generate method ({self.generate_method_name})'. "
                f"This could hence cause an error."
            )
        # Adding the always necessary base parameters to kwargs. They are updated if erroneously
        # introduced via the user-provided kwargs.
        prepared_kwargs.update(
            {
                CONFIG_FILE_KEY_GENERATE_ARGS_MODEL_FILE: model_file,
                CONFIG_FILE_KEY_GENERATE_ARGS_NUM_SAMPLES: num_samples,
                CONFIG_FILE_KEY_GENERATE_ARGS_OUTPUT_PATH: output_path,
                CONFIG_FILE_KEY_GENERATE_ARGS_SAVE_IMAGES: save_images,
            }
        )
        return prepared_kwargs

    def __repr__(self):
        return (
            f"ModelExecutor(model_id={self.model_id}, name={self.model_name}, package={self.package_name}, "
            f"image_size={self.image_size}, dependencies={self.dependencies}, link={self.package_link}, "
            f"path={self.serialised_model_file_path}, generate_method={self.generate_method_name}, "
            f"generate_method_args={self.generate_method_args})"
        )

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
