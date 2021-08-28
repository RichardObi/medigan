# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" main test script to test the primary functions/classes/methods of the medigan module.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
.. codeauthor:: Noussair Lazrak <lazrak.noussair@gmail.com>
"""
# run with python -m tests.tests

import glob
import logging
import shutil
import sys
import unittest


class TestMediganMethods(unittest.TestCase):

    def setUp(self):
        ## unittest logger config
        # This logger on root level initialized via logging.getLogger() will also log all log events
        # from the medigan library. Pass a logger nake (e.g. __name__) instead if you only want logs from tests.py
        self.logger = logging.getLogger()  # (__name__)
        self.logger.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        self.model_id_1 = "8f933c5e-72fc-461a-a5cb-73cbe65af6fc"
        self.model_id_2 = "2d29d505-9fb7-4c4d-b81f-47976e2c7dbf"
        self.test_output_path1 = "test_output_path1"
        self.test_output_path2 = "test_output_path2"
        self.num_samples = 5
        self.test_medigan_imports()
        self.test_init_generators()

    def test_medigan_imports(self):
        try:
            import src.medigan
        except Exception as e:
            self.logger.error(f"test_medigan_imports error: {e}")
            raise e
        self.assertRaises(expected_exception=Exception)

    def test_init_generators(self):
        try:
            from src.medigan.generators import Generators
            self.generators = Generators()
        except Exception as e:
            self.logger.error(f"test_init_generators error: {e}")
            raise e
        self.assertRaises(expected_exception=Exception)

    def test_generate_methods(self):
        try:
            self.generators.generate(model_id=self.model_id_1, num_samples=self.num_samples,
                                     output_path=self.test_output_path1)

            self.generators.generate(model_id=self.model_id_2, num_samples=self.num_samples,
                                     output_path=self.test_output_path2)

        except Exception as e:
            self.logger.error(f"test_generate_methods error: {e}")
            raise e
        self.assertRaises(expected_exception=Exception)

        # check if the number of generated files of model_id_1 is as expected.
        file_list_1 = glob.glob(self.test_output_path1 + "/*")
        self.logger.info(f"{len(file_list_1)} == {self.num_samples}")
        self.assertTrue(len(file_list_1) == self.num_samples)

        # check if the number of generated files of model_id_2 is as expected.
        file_list_2 = glob.glob(self.test_output_path2 + "/*")
        self.logger.debug(f"{len(file_list_2)} == {self.num_samples}")
        self.assertTrue(len(file_list_2) == self.num_samples)
        self._remove_dir_and_contents()

    def test_generate_methods_with_additional_args(self):
        # At the moment, no optional test_dict params are implemented in the model's generate methods.
        # TODO Add some valid key value pairs into test_dicts below and test.
        test_dict_1 = {}
        test_dict_2 = {}
        try:
            self.generators.generate(model_id=self.model_id_1, num_samples=self.num_samples,
                                     output_path=self.test_output_path1, **test_dict_1)

            self.generators.generate(model_id=self.model_id_2, num_samples=self.num_samples,
                                     output_path=self.test_output_path2, **test_dict_2)

        except Exception as e:
            self.logger.error(f"test_generate_methods_with_additional_args error: {e}")
            raise e
        self.assertRaises(expected_exception=Exception)
        self._check_if_samples_were_generated()
        self._remove_dir_and_contents()

    def test_get_generate_method(self):
        try:
            gen_function_1 = self.generators.get_generate_function(model_id=self.model_id_1,
                                                                   num_samples=self.num_samples)
            gen_function_1()
            self.logger.debug(
                f"Generated {self.num_samples} samples with the gen_function for model_id {self.model_id_1}")

            gen_function_2 = self.generators.get_generate_function(model_id=self.model_id_2,
                                                                   num_samples=self.num_samples)
            gen_function_2()
            self.logger.debug(
                f"Generated {self.num_samples} samples with the gen_function for model_id {self.model_id_2}")
        except Exception as e:
            self.logger.error(f"test_get_generate_method error: {e}")
            raise e
        self.assertRaises(expected_exception=Exception)
        self._check_if_samples_were_generated()
        self._remove_dir_and_contents()

    def test_search_for_models_method(self):
        try:
            values_list = ['dcgan', 'mMg', 'ClF', 'modalities']
            models = self.generators.find_matching_models_by_values(values=values_list, target_values_operator='AND',
                                                                    are_keys_also_matched=True, is_case_sensitive=False)
            self.logger.debug(f'For value {values_list}, these models were found: {models}')
            self.assertTrue(len(models) > 0)

            values_list = ['DCGAN', 'Mammography']
            models = self.generators.find_matching_models_by_values(values=values_list, target_values_operator='OR',
                                                                    are_keys_also_matched=False, is_case_sensitive=True)
            self.logger.debug(f'For value {values_list}, these models were found: {models}')
            self.assertTrue(len(models) > 0)
        except Exception as e:
            self.logger.error(f"test_search_for_models_method error: {e}")
            raise e
        self.assertRaises(expected_exception=Exception)

    def test_find_model_and_generate_method(self):
        try:
            # For the values_list below exactly 1 model should be found due to inbreast (27.08.2021)
            values_list = ['dcgan', 'mMg', 'ClF', 'modalities', 'inbreast']
            self.generators.find_model_and_generate(values=values_list, target_values_operator='AND',
                                                    are_keys_also_matched=True,
                                                    is_case_sensitive=False, num_samples=self.num_samples)

            # For the values_list below exactly 1 model should be found due to optimam (27.08.2021)
            values_list = ['dcgan', 'mMg', 'ClF', 'inbreast', 'optimam']
            self.generator.find_model_and_generate(values=values_list, target_values_operator='AND',
                                                   are_keys_also_matched=True,
                                                   is_case_sensitive=False, num_samples=self.num_samples)
        except Exception as e:
            self.logger.error(f"test_find_model_and_generate_method error: {e}")
            raise e
        self._check_if_samples_were_generated()
        self._remove_dir_and_contents()

        try:
            # For the values_list below at least 2 models should be found. There should be no synthetic data generated in this case.
            values_list = ['dcgan', 'mMg', 'ClF', 'modalities']
            self.generator.find_model_and_generate(values=values_list, target_values_operator='AND',
                                                   are_keys_also_matched=True,
                                                   is_case_sensitive=False, num_samples=self.num_samples)
        except Exception as e:
            self.logger.error(f"test_find_model_and_generate_method error: {e}")
            raise e
        self._check_if_samples_were_generated(should_sample_be_generated=False)
        self._remove_dir_and_contents()
        self.assertRaises(expected_exception=Exception)

    def test_find_and_rank_models_then_generate_method(self):
        try:
            # TODO This might not work if there are no respective metrics for any of these models in the global json file.
            # These values would need to find at least two models
            values_list = ['dcgan', 'MMG']  # , 'inbreast']
            self.generators.find_models_rank_and_generate(values=values_list, target_values_operator='AND',
                                                          are_keys_also_matched=True,
                                                          is_case_sensitive=False, metric="SSIM", order="asc",
                                                          num_samples=self.num_samples)
            self.generators.find_models_rank_and_generate(values=values_list, target_values_operator='AND',
                                                          are_keys_also_matched=True,
                                                          is_case_sensitive=False, metric="SSIM", order="desc",
                                                          num_samples=self.num_samples)
        except Exception as e:
            self.logger.error(f"test_find_and_rank_models_then_generate_method error: {e}")
            raise e
        self._check_if_samples_were_generated()
        self._remove_dir_and_contents()
        self.assertRaises(expected_exception=Exception)

    def _check_if_samples_were_generated(self, should_sample_be_generated: bool = True):
        if should_sample_be_generated:
            # check if the number of generated samples of model_id_1 is as expected.
            file_list_1 = glob.glob(self.test_output_path1 + "/*")
            # self.logger.debug(f"{len(file_list_1)} == {self.num_samples}")
            self.assertTrue(len(file_list_1) == self.num_samples)

            # check if the number of generated samples of model_id_2 is as expected.
            file_list_2 = glob.glob(self.test_output_path2 + "/*")
            # self.logger.debug(f"{len(file_list_2)} == {self.num_samples}")
            self.assertTrue(len(file_list_2) == self.num_samples)
        else:
            # check if the sample have NOT been generated for model_id 1 and 2
            file_list_1 = glob.glob(self.test_output_path1 + "/*")
            # self.logger.debug(f"{len(file_list_1)} == {self.num_samples}")
            self.assertTrue(len(file_list_1) != self.num_samples)

            file_list_2 = glob.glob(self.test_output_path2 + "/*")
            # self.logger.debug(f"{len(file_list_2)} == {self.num_samples}")
            self.assertTrue(len(file_list_2) != self.num_samples)

    def _remove_dir_and_contents(self):
        # After each test, empty the created folders and files to avoid corrupting a new test.
        try:
            shutil.rmtree(self.test_output_path1)
            shutil.rmtree(self.test_output_path2)
        except OSError as e:
            self.logger.error("Error: %s - %s." % (e.filename, e.strerror))


if __name__ == '__main__':
    unittest.main()
