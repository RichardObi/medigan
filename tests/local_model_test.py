# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" Script for testing of a localModel object initialization and usage in medigan.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""
# run with python -m tests.local_model_test


import logging
import unittest


class MyTestCase(unittest.TestCase):
    def test_local_model(self):

        ######### Local Model Init Parameters #########
        ## These are examples, please adjust to your needs.
        path_to_script_w_generate_function = (
            "some_folder/another_folder/generate_samples.py"
        )
        # "some_folder/another_folder/generate_samples.py"
        are_optional_config_fields_requested: bool = False  # True
        is_metadata_file_updated: bool = False

        # metadata_path param:
        # Note: Also test with the metadata_path being set to None. Only then, the other params are considered.
        metadata_path: str = (
            None  # "/Users/richardosuala/Desktop/MMG_MASS_BCDR_DCGAN/metadata.json"
        )

        # Other metadata params - no need for them if you already provide a metadata_path to a json file containing them
        model_id: str = "00012_DCGAN_MMG_MASS_ROI"
        package_link: str = "/Users/richardosuala/Desktop/MMG_MASS_BCDR_DCGAN"
        model_name: str = "500"
        model_extension: str = ".pt"
        generate_method_name: str = ""  # "generate"
        package_name: str = "DCGAN_MMG"
        image_size: list = []
        dependencies: list = []

        try:
            from src.medigan.generators import Generators

            generators = Generators()
            local_model = generators.create_local_model(
                model_id=model_id,
                package_link=package_link,
                model_name=model_name,
                model_extension=model_extension,
                generate_method_name=generate_method_name,
                image_size=image_size,
                dependencies=dependencies,
                package_name=package_name,
                metadata_path=metadata_path,
                path_to_script_w_generate_function=path_to_script_w_generate_function,
                are_optional_config_fields_requested=are_optional_config_fields_requested,
                is_metadata_file_updated=is_metadata_file_updated,
            )
        except Exception as e:
            logging.error(f"test_local_model error during local model creation: {e}")
            raise e

        try:
            generators.generate_with_local_model(local_model=local_model)
        except Exception as e:
            logging.error(
                f"test_local_model error during generating samples with local model: {e}"
            )
            raise e
        self.assertRaises(Exception)


if __name__ == "__main__":
    unittest.main()
