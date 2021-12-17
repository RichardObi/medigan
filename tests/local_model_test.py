# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" script for testing of a localModel object initialization and usage in medigan.
.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""
# run with python -m tests.local_model_test


import logging
import unittest


class MyTestCase(unittest.TestCase):
    def test_local_model(self):


        ######### Local Model Init Parameters #########
        ## These are examples, please adjust.
        model_id: str = "00005_DCGAN_MMG_MASS_ROI"
        package_link: str = "/None/None/"
        model_name: str = "weights"
        model_extension: str = ".pt"
        generate_method_name: str = "generate_abc"
        metadata_path: str = "/Users/richardosuala/Desktop/MMG_MASS_BCDR_DCGAN/metadata.json"
        package_name: str = None
        image_size: list = []
        dependencies: list = []
        generate_function_script_path: str = None
        are_optional_config_fields_requested: bool = True
        is_added_to_config: bool = True
        is_metadata_file_updated: bool = True

        ######### Generate with Local Model Parameters #########
        # MODEL_ID = "YOUR_MODEL_ID_HERE"
        # NUM_SAMPLES = 10
        # OUTPUT_PATH = f"output/{MODEL_ID}/"

        try:
            from src.medigan.generators import Generators
            generators = Generators()
            generators.create_local_model(model_id=model_id, package_link=package_link, model_name=model_name,
                                          model_extension=model_extension,
                                          generate_method_name=generate_method_name,
                                          image_size=image_size, dependencies=dependencies, package_name=package_name,
                                          metadata_path=metadata_path,
                                          generate_function_script_path=generate_function_script_path,
                                          are_optional_config_fields_requested=are_optional_config_fields_requested,
                                          is_added_to_config=is_added_to_config,
                                          is_metadata_file_updated=is_metadata_file_updated)

        except Exception as e:
            logging.error(f"test_init_generators error: {e}")
            raise e
        self.assertRaises(Exception)


if __name__ == '__main__':
    unittest.main()
