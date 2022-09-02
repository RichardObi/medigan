# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" main test script to test the primary functions/classes/methods. """
# run with python -m tests.test_generator

import glob
import logging
import os
import shutil
import sys

import pytest
import torch

# import unittest


# Set the logging level depending on the level of detail you would like to have in the logs while running the tests.
LOGGING_LEVEL = logging.INFO  # WARNING  # logging.INFO

models_with_args = [
    (
        "00001_DCGAN_MMG_CALC_ROI",
        {},
        100,
    ),  # 100 samples to test automatic batch-wise image generation in model_executor
    ("00002_DCGAN_MMG_MASS_ROI", {}, 3),
    ("00003_CYCLEGAN_MMG_DENSITY_FULL", {"translate_all_images": False}, 2),
    (
        "00004_PIX2PIX_MASKTOMASS_BREAST_MG_SYNTHESIS",
        {
            "shapes": ["oval"],
            "ssim_threshold": 0.18,
            "image_size": [128, 128],
            "patch_size": [30, 30],
        },
        3,
    ),
    ("00005_DCGAN_MMG_MASS_ROI", {}, 3),
    ("00006_WGANGP_MMG_MASS_ROI", {}, 3),
    (
        "00007_INPAINT_BRAIN_MRI",
        {
            "image_size": (256, 256),
            "num_inpaints_per_sample": 2,
            "randomize_input_image_order": False,
            "add_variations_to_mask": False,
            "x_center": 120,
            "y_center": 140,
            "radius_1": 8,
            "radius_2": 12,
            "radius_3": 24,
        },
        3,
    ),
    ("00008_C-DCGAN_MMG_MASSES", {"condition": 0}, 3),
    ("00009_PGGAN_POLYP_PATCHES_W_MASKS", {"save_option": "image_only"}, 3),
    ("00010_FASTGAN_POLYP_PATCHES_W_MASKS", {"save_option": "image_only"}, 3),
    ("00011_SINGAN_POLYP_PATCHES_W_MASKS", {"checkpoint_ids": [999]}, 3),
    ("00012_C-DCGAN_MMG_MASSES", {"condition": 0}, 3),
    ("00013_CYCLEGAN_MMG_DENSITY_OPTIMAM_MLO", {"translate_all_images": False}, 2),
    ("00014_CYCLEGAN_MMG_DENSITY_OPTIMAM_CC", {"translate_all_images": False}, 2),
    ("00015_CYCLEGAN_MMG_DENSITY_CSAW_MLO", {"translate_all_images": False}, 2),
    ("00016_CYCLEGAN_MMG_DENSITY_CSAW_CC", {"translate_all_images": False}, 2),
    ("00017_DCGAN_XRAY_LUNG_NODULES", {}, 3),
    ("00018_WGANGP_XRAY_LUNG_NODULES", {}, 3),
    ("00019_PGGAN_CHEST_XRAY", {}, 3),
]

# class TestMediganExecutorMethods(unittest.TestCase):
class TestMediganExecutorMethods:
    def setup_class(self):
        ## unittest logger config
        # This logger on root level initialized via logging.getLogger() will also log all log events
        # from the medigan library. Pass a logger name (e.g. __name__) instead if you only want logs from tests.py
        self.logger = logging.getLogger()  # (__name__)
        self.logger.setLevel(LOGGING_LEVEL)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(LOGGING_LEVEL)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        self.test_output_path = "test_output_path"
        self.num_samples = 2
        self.test_imports_and_init_generators(self)
        self._remove_dir_and_contents(self)  # in case something is left there.
        self.model_ids = self.generators.config_manager.model_ids

    def test_imports_and_init_generators(self):
        from src.medigan.constants import (
            CONFIG_FILE_KEY_EXECUTION,
            CONFIG_FILE_KEY_GENERATE,
            CONFIG_FILE_KEY_GENERATE_ARGS_INPUT_LATENT_VECTOR_SIZE,
        )
        from src.medigan.generators import Generators

        self.generators = Generators()
        self.CONFIG_FILE_KEY_EXECUTION = CONFIG_FILE_KEY_EXECUTION
        self.CONFIG_FILE_KEY_GENERATE = CONFIG_FILE_KEY_GENERATE
        self.CONFIG_FILE_KEY_GENERATE_ARGS_INPUT_LATENT_VECTOR_SIZE = (
            CONFIG_FILE_KEY_GENERATE_ARGS_INPUT_LATENT_VECTOR_SIZE
        )

    @pytest.mark.parametrize("models_with_args", [models_with_args])
    def test_sample_generation_methods(self, models_with_args: list):

        self.logger.debug(f"models: {models_with_args}")
        for i, model_id in enumerate(self.model_ids):
            self._remove_dir_and_contents()  # Already done in each test independently, but to be sure, here again.
            self.test_generate_method(model_id=model_id)

            # Check if args available fo model_id. Note: The models list may not include the latest medigan models
            for model in models_with_args:
                if model_id == model[0]:
                    self.test_generate_method_with_additional_args(
                        model_id=model[0], args=model[1], expected_num_samples=model[2]
                    )
            self.test_get_generate_method(model_id=model_id)
            self.test_get_dataloader_method(model_id=model_id)

            # if i == 16:  # just for local testing
            self._remove_model_dir_and_zip(
                model_ids=[model_id], are_all_models_deleted=False
            )

    @pytest.mark.parametrize(
        "values_list, should_sample_be_generated",
        [
            (["dcgan", "mMg", "ClF", "modality", "inbreast"], True),
            (["dcgan", "mMg", "ClF", "modality", "optimam"], True),
            (["dcgan", "mMg", "ClF", "modalities"], False),
        ],
    )
    def test_find_model_and_generate_method(
        self, values_list, should_sample_be_generated
    ):
        self._remove_dir_and_contents()

        self.generators.find_model_and_generate(
            values=values_list,
            target_values_operator="AND",
            are_keys_also_matched=True,
            is_case_sensitive=False,
            num_samples=self.num_samples,
            output_path=self.test_output_path,
        )

        self._check_if_samples_were_generated(
            should_sample_be_generated=should_sample_be_generated
        )

    @pytest.mark.parametrize(
        "values_list, metric",
        [
            (["dcgan", "MMG"], "downstream_task.CLF.trained_on_real_and_fake.f1"),
            (["dcgan", "MMG"], "turing_test.AUC"),
        ],
    )
    def test_find_and_rank_models_then_generate_method(self, values_list, metric):
        self._remove_dir_and_contents()
        # TODO This test needs the respective metrics for any of these models to be available in config/global.json.
        # These values would need to find at least two models.
        self.generators.find_models_rank_and_generate(
            values=values_list,
            target_values_operator="AND",
            are_keys_also_matched=True,
            is_case_sensitive=False,
            metric=metric,
            order="asc",
            num_samples=self.num_samples,
            output_path=self.test_output_path,
        )
        self._check_if_samples_were_generated()

    # @pytest.mark.parametrize("model_id", [model[0] for model in models_with_args])
    @pytest.mark.skip
    def test_generate_method(self, model_id):
        self._remove_dir_and_contents()
        self.generators.generate(
            model_id=model_id,
            num_samples=self.num_samples,
            output_path=self.test_output_path,
        )
        self._check_if_samples_were_generated()

    # @pytest.mark.parametrize("model_id, args, expected_num_samples", models_with_args)
    @pytest.mark.skip
    def test_generate_method_with_additional_args(
        self, model_id, args, expected_num_samples
    ):
        self._remove_dir_and_contents()
        self.generators.generate(
            model_id=model_id,
            num_samples=expected_num_samples,
            output_path=self.test_output_path,
            **args,
        )
        self._check_if_samples_were_generated(num_samples=expected_num_samples)

    # @pytest.mark.parametrize("model_id", [model[0] for model in models_with_args])
    @pytest.mark.skip
    def test_get_generate_method(self, model_id):
        self._remove_dir_and_contents()
        gen_function = self.generators.get_generate_function(
            model_id=model_id,
            num_samples=self.num_samples,
            output_path=self.test_output_path,
        )
        gen_function()
        self._check_if_samples_were_generated()
        del gen_function

    # @pytest.mark.parametrize("model_id", [model[0] for model in models_with_args])
    @pytest.mark.skip
    def test_get_dataloader_method(self, model_id="00007_INPAINT_BRAIN_MRI"):
        self._remove_dir_and_contents()
        data_loader = self.generators.get_as_torch_dataloader(
            model_id=model_id, num_samples=self.num_samples
        )
        self.logger.debug(f"len(data_loader): {len(data_loader)}")
        #### Get the object at index 0 from the dataloader
        data_dict = next(iter(data_loader))

        # Test if the items at index [0] of the aforementioned object is of type torch tensor (e.g. torch.uint8) and not None, as expected by data structure design decision.
        assert torch.is_tensor(data_dict.get("sample"))

        # Test if the items at index [1], [2] of the aforementioned object are None and, if not, whether they are of type torch tensor, as expected
        assert data_dict.get("mask") is None or torch.is_tensor(data_dict.get("mask"))
        assert data_dict.get("other_imaging_output") is None or torch.is_tensor(
            data_dict.get("other_imaging_output")
        )

        # Test if the items at index [3] of the aforementioned object is None and, if not, whether it is of type list of strings, as expected.
        assert data_dict.get("label") is None or (
            isinstance(data_dict.get("label"), list)
            and isinstance(data_dict.get("label")[0], str)
        )
        del data_dict
        del data_loader

    # @pytest.mark.parametrize("model_id", [model[0] for model in models_with_args])
    @pytest.mark.skip
    def test_visualize_method(self, model_id):

        if (
            self.CONFIG_FILE_KEY_GENERATE_ARGS_INPUT_LATENT_VECTOR_SIZE
            in self.generators.config_manager.config_dict[model_id][
                self.CONFIG_FILE_KEY_EXECUTION
            ][self.CONFIG_FILE_KEY_GENERATE]
        ):

            self.generators.visualize(model_id, auto_close=True)

        else:
            with pytest.raises(Exception) as e:

                self.generators.visualize(model_id, auto_close=True)

                assert e.type == ValueError

    @pytest.mark.skip
    def _check_if_samples_were_generated(
        self, num_samples=None, should_sample_be_generated: bool = True
    ):
        # check if the number of generated samples of model_id_1 is as expected.
        file_list = glob.glob(self.test_output_path + "/*")
        self.logger.debug(f"{len(file_list)} == {self.num_samples} ?")
        if num_samples is None:
            num_samples = self.num_samples

        if should_sample_be_generated:
            assert (
                len(file_list) == num_samples
                or len(file_list)
                == num_samples
                * 2
                * 6  # 00007_INPAINT_BRAIN_MRI: 2 inpaints per sample, 6 outputs per sample
                or len(file_list) == num_samples * 2
                or len(file_list) == num_samples + 1
            )  # Temporary fix for different outputs per model.
            # Some models are balanced per label by default: If num_samples is odd, then len(file_list)==num_samples +1
        else:
            assert len(file_list) == 0

    # @pytest.mark.skip
    def _remove_dir_and_contents(self):
        """After each test, empty the created folders and files to avoid corrupting a new test."""

        try:
            shutil.rmtree(self.test_output_path)
        except OSError as e:
            # This may give an error if the folders are not created.
            self.logger.debug(
                f"Exception while trying to delete folder. Likely it simply had not yet been created: {e}"
            )
        except Exception as e2:
            self.logger.error(f"Error while trying to delete folder: {e2}")

    @pytest.mark.skip
    def _remove_model_dir_and_zip(
        self, model_ids=[], are_all_models_deleted: bool = False
    ):
        """After a specific model folders, model_executor, and model zip file to avoid running out-of-disk space."""

        try:
            for i, model_executor in enumerate(self.generators.model_executors):
                if model_executor.model_id in model_ids or are_all_models_deleted:
                    try:
                        # Delete the folder containing the model
                        model_path = os.path.dirname(
                            model_executor.deserialized_model_as_lib.__file__
                        )
                        shutil.rmtree(model_path)
                        self.logger.info(
                            f"Deleted directory of model {model_executor.model_id}. ({model_path})"
                        )

                    except OSError as e:
                        # This may give an error if the FOLDER is not present
                        self.logger.warning(
                            f"Exception while trying to delete the model folder of model {model_executor.model_id}: {e}"
                        )
                    try:
                        # If the downloaded zip package of the model was not deleted inside the model_path, we explicitely delete it now.
                        if model_executor.package_path.is_file():
                            os.remove(model_executor.package_path)
                            self.logger.info(
                                f"Deleted zip file of model {model_executor.model_id}. ({model_executor.package_path})"
                            )
                    except Exception as e:
                        self.logger.warning(
                            f"Exception while trying to delete the ZIP file ({model_executor.package_path}) of model {model_executor.model_id}: {e}"
                        )
            # Deleting the stateful model_executors instantiated by the generators module, after deleting folders and zips
            if are_all_models_deleted:
                self.generators.model_executors.clear()
            else:
                for model_id in model_ids:
                    model_executor = self.generators.find_model_executor_by_id(model_id)
                    if model_executor is not None:
                        self.generators.model_executors.remove(model_executor)
                    del model_executor
        except Exception as e2:
            self.logger.error(
                f"Error while trying to delete model folders and zips: {e2}"
            )

    # @pytest.fixture(scope="session", autouse=True)
    def teardown_class(self):
        """After all tests, empty the large model folders, model_executors, and zip files to avoid running out-of-disk space."""

        # yield is at test-time, signaling that things after yield are run after the execution of the last test has terminated
        # https://docs.pytest.org/en/7.1.x/reference/reference.html?highlight=fixture#pytest.fixture
        # yield None

        # Remove all test outputs in test_output_path
        self._remove_dir_and_contents(self)

        # Remove all model folders, zip files and model executors
        # self._remove_model_dir_and_zip(
        #    self, model_ids=["00006_WGANGP_MMG_MASS_ROI"], are_all_models_deleted=False
        # )  # just for local testing
        self._remove_model_dir_and_zip(
            self, model_ids=None, are_all_models_deleted=True
        )
