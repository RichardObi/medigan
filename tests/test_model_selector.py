# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" main test script to test the primary functions/classes/methods. """
# run with python -m tests.test_generator

import logging
import sys

import pytest

# import unittest


# Set the logging level depending on the level of detail you would like to have in the logs while running the tests.
LOGGING_LEVEL = logging.INFO  # WARNING  # logging.INFO

models = [
    (
        "00001_DCGAN_MMG_CALC_ROI",
        {},
        100,
    ),
    ("00002_DCGAN_MMG_MASS_ROI", {}, 3),
    ("00003_CYCLEGAN_MMG_DENSITY_FULL", {"translate_all_images": False}, 2),
    ("00005_DCGAN_MMG_MASS_ROI", {}, 3),
    # Further models can be added here if/when needed.
]

# class TestMediganSelectorMethods(unittest.TestCase):
class TestMediganSelectorMethods:
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
        self.test_init_generators()

    def test_init_generators(self):
        from src.medigan.generators import Generators

        self.generators = Generators()

    @pytest.mark.parametrize(
        "values_list",
        [
            (["dcgan", "mMg", "ClF", "modality"]),
            (["DCGAN", "Mammography"]),
        ],
    )
    def test_search_for_models_method(self, values_list):
        found_models = self.generators.find_matching_models_by_values(
            values=values_list,
            target_values_operator="AND",
            are_keys_also_matched=True,
            is_case_sensitive=False,
        )
        self.logger.debug(
            f"For value {values_list}, these models were found: {found_models}"
        )
        assert len(found_models) > 0

    @pytest.mark.parametrize(
        "models, values_list, metric",
        [
            (
                models,
                ["dcgan", "MMG"],
                "CLF.trained_on_real_and_fake.f1",
            ),
            (models, ["dcgan", "MMG"], "turing_test.AUC"),
        ],
    )
    def test_find_and_rank_models_by_performance(self, models, values_list, metric):
        # These values would need to find at least two models. See metrics and values in the config/global.json file.
        found_ranked_models = self.generators.find_models_and_rank(
            values=values_list,
            target_values_operator="AND",
            are_keys_also_matched=True,
            is_case_sensitive=False,
            metric=metric,
            order="desc",
        )
        assert (
            len(found_ranked_models) > 0  # some models were found as is expected
            and found_ranked_models[0]["model_id"] is not None  # has a model id
            and (
                len(found_ranked_models) < 2
                or found_ranked_models[0][metric] > found_ranked_models[1][metric]
            )  # descending order (the higher a model's value, the lower its index in the list) is working
        )

    @pytest.mark.parametrize(
        "models, metric, order",
        [
            (
                models,
                "FID",
                "asc",
            ),  # Note: normally a lower FID is better, therefore asc (model with lowest FID has lowest result list index).
            (
                models,
                "FID_RADIMAGENET_ratio",
                "desc",  # descending, as the higher the FID ratio the better.
            ),
            # Note: normally a lower FID is better, therefore asc (model with lowest FID has lowest result list index).
            (models, "CLF.trained_on_real_and_fake.f1", "desc"),
            (models, "turing_test.AUC", "desc"),
        ],
    )
    def test_rank_models_by_performance(self, models, metric, order):
        """Ranking according to metrics in the config/global.json file."""
        ranked_models = self.generators.rank_models_by_performance(
            model_ids=[models[1][0], models[2][0]],
            metric=metric,
            order=order,
        )
        assert (
            len(ranked_models) > 0  # at least one model was found
            and (
                len(ranked_models) >= 21 or metric != "FID"
            )  # we should find at least 21 models with FID in medigan
            and ranked_models[0]["model_id"]
            is not None  # found model has a model id (i.e. correctly formatted results)
            and (
                len(ranked_models) == 1
                or (
                    ranked_models[0][metric] > ranked_models[1][metric]
                    or metric == "FID"
                )
            )  # descending order (the higher a model's value, the lower its index in the list) is working. In case of FID it is the other way around (ascending order is better).
        )

    @pytest.mark.parametrize(
        "key1, value1, expected",
        [
            ("modality", "Full-Field Mammography", 2),
            ("license", "BSD", 2),
            ("performance.CLF.trained_on_real_and_fake.f1", "0.96", 0),
            ("performance.turing_test.AUC", "0.56", 0),
        ],
    )
    def test_get_models_by_key_value_pair(self, key1, value1, expected):
        found_models = self.generators.get_models_by_key_value_pair(
            key1=key1, value1=value1, is_case_sensitive=False
        )
        assert len(found_models) >= expected
