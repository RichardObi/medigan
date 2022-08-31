# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" main test script for model visualization functions/classes/methods. """
# run with python -m tests.test_model_visualizer

import pytest

from src.medigan.constants import (CONFIG_FILE_KEY_EXECUTION,
                                   CONFIG_FILE_KEY_GENERATE,
                                   CONFIG_FILE_KEY_GENERATE_ARGS_INPUT_LATENT_VECTOR_SIZE)
from src.medigan.generators import Generators

generators = Generators()
config_manager = generators.config_manager
models = config_manager.model_ids
config = config_manager.config_dict


class TestModelVisualizer:
    @pytest.mark.parametrize("model_id", models)
    def test_visualize(self, model_id):
        if (
            CONFIG_FILE_KEY_GENERATE_ARGS_INPUT_LATENT_VECTOR_SIZE
            in config[model_id][CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_GENERATE]
        ):

            generators.visualize(model_id, auto_close=True)

        else:
            with pytest.raises(Exception) as e:

                generators.visualize(model_id, auto_close=True)

                assert e.type == ValueError
