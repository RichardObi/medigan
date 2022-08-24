# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" main test script to test the primary functions/classes/methods. """
# run with python -m tests.test_generator

import glob
import logging
import shutil
import sys
import unittest

import pytest

# Set the logging level depending on the level of detail you would like to have in the logs while running the tests.
LOGGING_LEVEL = logging.WARNING  # logging.INFO

models = [
    ("00001_DCGAN_MMG_CALC_ROI", {}, 3),
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
    ("00007_BEZIERCURVE_TUMOUR_MASK", {"shapes": ["oval"]}, 3),
    ("00008_C-DCGAN_MMG_MASSES", {"condition": 0}, 3),
    ("00009_PGGAN_POLYP_PATCHES_W_MASKS", {"save_option": "image_only"}, 3),
    ("00010_FASTGAN_POLYP_PATCHES_W_MASKS", {"save_option": "image_only"}, 3),
    ("00011_SINGAN_POLYP_PATCHES_W_MASKS", {"checkpoint_ids": [999]}, 3),
    # ("00012_C-DCGAN_MMG_MASSES", {"condition": 0}, 3),
    # ("00013_CYCLEGAN_MMG_DENSITY_OPTIMAM_MLO", {"translate_all_images": False}, 2),
    # ("00014_CYCLEGAN_MMG_DENSITY_OPTIMAM_CC", {"translate_all_images": False}, 2),
    # ("00015_CYCLEGAN_MMG_DENSITY_CSAW_MLO", {"translate_all_images": False}, 2),
    # ("00016_CYCLEGAN_MMG_DENSITY_CSAW_CC", {"translate_all_images": False}, 2),
    # ("00017_DCGAN_XRAY_LUNG_NODULES", {}, 3),
    # ("00018_WGANGP_XRAY_LUNG_NODULES", {}, 3),
    # ("00019_PGGAN_CHEST_XRAY", {}, 3),
]

# class TestMediganMethods(unittest.TestCase):
class TestMediganMethods:
    def setup_method(self):

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
        self.num_samples = 1
        self.test_medigan_imports()
        self.test_init_generators()
        self._remove_dir_and_contents()  # in case something is left there.

    def test_medigan_imports(self):
        import src.medigan

    def test_init_generators(self):
        from src.medigan.generators import Generators

        self.generators = Generators()

    @pytest.mark.parametrize("model_id", [model[0] for model in models])
    def test_generate_method(self, model_id):
        self._remove_dir_and_contents()
        self.generators.generate(
            model_id=model_id,
            num_samples=self.num_samples,
            output_path=self.test_output_path,
        )
        self._check_if_samples_were_generated()

    @pytest.mark.parametrize("model_id, args, expected_num_samples", models)
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

    @pytest.mark.parametrize("model_id", [model[0] for model in models])
    def test_get_generate_method(self, model_id):
        self._remove_dir_and_contents()
        gen_function = self.generators.get_generate_function(
            model_id=model_id,
            num_samples=self.num_samples,
            output_path=self.test_output_path,
        )

        gen_function()

        self._check_if_samples_were_generated()

    def test_search_for_models_method(self):
        values_list = ["dcgan", "mMg", "ClF", "modality"]
        models = self.generators.find_matching_models_by_values(
            values=values_list,
            target_values_operator="AND",
            are_keys_also_matched=True,
            is_case_sensitive=False,
        )
        self.logger.debug(f"For value {values_list}, these models were found: {models}")
        assert len(models) > 0

        values_list = ["DCGAN", "Mammography"]
        models = self.generators.find_matching_models_by_values(
            values=values_list,
            target_values_operator="OR",
            are_keys_also_matched=False,
            is_case_sensitive=True,
        )
        self.logger.debug(f"For value {values_list}, these models were found: {models}")
        assert len(models) > 0

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

    @pytest.mark.parametrize(
        "values_list, metric",
        [(["dcgan", "MMG"], "downstream_task.CLF.trained_on_real_and_fake.f1")],
    )
    def test_find_and_rank_models_by_performance(self, values_list, metric):
        # These values would need to find at least two models. See metrics and values in the config/global.json file.
        model_list = self.generators.find_models_and_rank(
            values=values_list,
            target_values_operator="AND",
            are_keys_also_matched=True,
            is_case_sensitive=False,
            metric=metric,
            order="asc",
        )
        assert len(model_list) > 0 and model_list[0]["model_id"] == models[1][0]

    @pytest.mark.parametrize(
        "metric, order",
        [
            ("downstream_task.CLF.trained_on_real_and_fake.f1", "desc"),
            ("turing_test.AUC", "desc"),
        ],
    )
    def test_rank_models_by_performance(self, metric, order):
        # See metrics in the config/global.json file.
        ranked_models = self.generators.rank_models_by_performance(
            model_ids=[models[1][0], models[2][0]],
            metric=metric,
            order=order,
        )
        assert len(ranked_models) > 0 and ranked_models[0]["model_id"] == models[1][0]

    @pytest.mark.parametrize(
        "key1, value1, expected",
        [
            ("modality", "Full-Field Mammography", 2),
            ("license", "BSD", 2),
            ("performance.downstream_task.CLF.trained_on_real_and_fake.f1", "0.89", 0),
            ("performance.turing_test.AUC", "0.56", 0),
        ],
    )
    def test_get_models_by_key_value_pair(self, key1, value1, expected):
        found_models = self.generators.get_models_by_key_value_pair(
            key1=key1, value1=value1, is_case_sensitive=False
        )

        assert len(found_models) >= expected

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
                or len(file_list) == num_samples * 2
                or len(file_list) == num_samples + 1
            )  # Temporary fix for different outputs per model.
            # Some models are balanced per label by default: If num_samples is odd, then len(file_list)==num_samples +1
        else:
            assert len(file_list) == 0

    def _remove_dir_and_contents(self):
        # After each test, empty the created folders and files to avoid corrupting a new test.
        try:
            shutil.rmtree(self.test_output_path)
        except OSError as e:
            # This may give an error if the folders are not created.
            self.logger.debug(
                f"Exception while trying to delete folder. Likely it simply had not yet been created: {e}"
            )
        except Exception as e2:
            self.logger.error(f"Error while trying to delete folder: {e2}")
