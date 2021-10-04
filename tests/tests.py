# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" main test script to test the primary functions/classes/methods of the medigan module.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""
# run with python -m tests.tests

import glob
import logging
import shutil
import sys
import unittest

# Set the logging level depending on the level of detail you would like to have in the logs while running the tests.
LOGGING_LEVEL = logging.ERROR  # logging.INFO

class TestMediganMethods(unittest.TestCase):

    def setUp(self):

        ## unittest logger config
        # This logger on root level initialized via logging.getLogger() will also log all log events
        # from the medigan library. Pass a logger name (e.g. __name__) instead if you only want logs from tests.py
        self.logger = logging.getLogger()  # (__name__)
        self.logger.setLevel(LOGGING_LEVEL)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(LOGGING_LEVEL)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        self.model_id_1 = "00001_DCGAN_MMG_CALC_ROI"
        self.model_id_2 = "00002_DCGAN_MMG_MASS_ROI"
        self.model_id_3 = "00003_CYCLEGAN_MMG_DENSITY_FULL"
        self.test_output_path1 = "test_output_path1"
        self.test_output_path2 = "test_output_path2"
        self.test_output_path3 = "test_output_path3"
        self.num_samples = 5
        self.test_medigan_imports()
        self.test_init_generators()
        self._remove_dir_and_contents()  # in case something is left there.

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
        self._remove_dir_and_contents()
        try:
            self.generators.generate(model_id=self.model_id_1, num_samples=self.num_samples,
                                     output_path=self.test_output_path1)

            self.generators.generate(model_id=self.model_id_2, num_samples=self.num_samples,
                                     output_path=self.test_output_path2)

            self.generators.generate(model_id=self.model_id_3, num_samples=self.num_samples,
                                     output_path=self.test_output_path3)

        except Exception as e:
            self.logger.error(f"test_generate_methods error: {e}")
            raise e
        self.assertRaises(expected_exception=Exception)
        self._check_if_samples_were_generated(models=[1, 2, 3])

    def test_generate_methods_with_additional_args(self):
        self._remove_dir_and_contents()
        # At the moment, no optional test_dict params are implemented in the model's generate methods.
        # TODO: Feel free to add some valid key value pairs into test_dicts below and test generation.
        test_dict_1 = {}
        test_dict_2 = {}
        test_dict_3 = {"translate_all_images": True}
        try:
            self.generators.generate(model_id=self.model_id_1, num_samples=self.num_samples,
                                     output_path=self.test_output_path1, **test_dict_1)

            self.generators.generate(model_id=self.model_id_2, num_samples=self.num_samples,
                                     output_path=self.test_output_path2, **test_dict_2)

            self.generators.generate(model_id=self.model_id_3, num_samples=self.num_samples,
                                     output_path=self.test_output_path3, **test_dict_3)

        except Exception as e:
            self.logger.error(f"test_generate_methods_with_additional_args error: {e}")
            raise e
        self.assertRaises(expected_exception=Exception)
        self._check_if_samples_were_generated(models=[1, 2])
        # 17 example images are available for translation in model 3.
        self._check_if_samples_were_generated(models=[3], num_samples=17)

    def test_get_generate_method(self):
        self._remove_dir_and_contents()
        try:
            gen_function_1 = self.generators.get_generate_function(model_id=self.model_id_1,
                                                                   num_samples=self.num_samples,
                                                                   output_path=self.test_output_path1)
            gen_function_1()

            gen_function_2 = self.generators.get_generate_function(model_id=self.model_id_2,
                                                                   num_samples=self.num_samples,
                                                                   output_path=self.test_output_path2)
            gen_function_2()

            gen_function_3 = self.generators.get_generate_function(model_id=self.model_id_3,
                                                                   num_samples=self.num_samples,
                                                                   output_path=self.test_output_path3)
            gen_function_3()
        except Exception as e:
            self.logger.error(f"test_get_generate_method error: {e}")
            raise e
        self.assertRaises(expected_exception=Exception)
        self._check_if_samples_were_generated(models=[1, 2, 3])

    def test_search_for_models_method(self):
        try:
            values_list = ['dcgan', 'mMg', 'ClF', 'modality']
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
        self._remove_dir_and_contents()
        try:
            # For the values_list below exactly 1 model should be found due to inbreast (27.08.2021)
            values_list = ['dcgan', 'mMg', 'ClF', 'modality', 'inbreast']
            self.generators.find_model_and_generate(values=values_list, target_values_operator='AND',
                                                    are_keys_also_matched=True,
                                                    is_case_sensitive=False, num_samples=self.num_samples,
                                                    output_path=self.test_output_path1)

            # For the values_list below exactly 1 model should be found due to optimam (27.08.2021)
            values_list = ['dcgan', 'mMg', 'ClF', 'modality', 'optimam']
            self.generators.find_model_and_generate(values=values_list, target_values_operator='AND',
                                                    are_keys_also_matched=True,
                                                    is_case_sensitive=False, num_samples=self.num_samples,
                                                    output_path=self.test_output_path2)
        except Exception as e:
            self.logger.error(f"test_find_model_and_generate_method error: {e}")
            raise e
        self._check_if_samples_were_generated(models=[1, 2])
        self._remove_dir_and_contents()
        try:
            # For the values_list below at least 2 models should be found.
            # There should be no synthetic data generated in this case.
            values_list = ['dcgan', 'mMg', 'ClF', 'modalities']
            self.generators.find_model_and_generate(values=values_list, target_values_operator='AND',
                                                    are_keys_also_matched=True,
                                                    is_case_sensitive=False, num_samples=self.num_samples,
                                                    output_path=self.test_output_path1)
        except Exception as e:
            self.logger.error(f"test_find_model_and_generate_method error: {e}")
            raise e
        self._check_if_samples_were_generated(models=[1, 2], should_sample_be_generated=False)
        self.assertRaises(expected_exception=Exception)

    def test_find_and_rank_models_then_generate_method(self):
        self._remove_dir_and_contents()
        try:
            # TODO This test needs the respective metrics for any of these models to be available in config/global.json.
            # These values would need to find at least two models.
            values_list = ['dcgan', 'MMG']
            metric = "downstream_task.CLF.trained_on_real_and_fake.f1"
            self.generators.find_models_rank_and_generate(values=values_list, target_values_operator='AND',
                                                          are_keys_also_matched=True,
                                                          is_case_sensitive=False,
                                                          metric=metric,
                                                          order="asc",
                                                          num_samples=self.num_samples,
                                                          output_path=self.test_output_path1)
        except Exception as e:
            self.logger.error(f"test_find_and_rank_models_then_generate_method error: {e}")
            raise e
        self._check_if_samples_were_generated(models=[1])
        self._remove_dir_and_contents()
        try:
            values_list = ['dcgan', 'MMG']
            metric = "turing_test.AUC"
            self.generators.find_models_rank_and_generate(values=values_list, target_values_operator='AND',
                                                          are_keys_also_matched=True,
                                                          is_case_sensitive=False, metric=metric, order="desc",
                                                          num_samples=self.num_samples,
                                                          output_path=self.test_output_path1)
        except Exception as e:
            self.logger.error(f"test_find_and_rank_models_then_generate_method error: {e}")
            raise e
        self._check_if_samples_were_generated(models=[1])

        self.assertRaises(expected_exception=Exception)

    def test_find_and_rank_models_by_performance(self):
        try:
            # These values would need to find at least two models. See metrics and values in the config/global.json file.
            values_list = ['dcgan', 'MMG']
            metric = "downstream_task.CLF.trained_on_real_and_fake.f1"
            model_list = self.generators.find_models_and_rank(values=values_list, target_values_operator='AND',
                                                              are_keys_also_matched=True,
                                                              is_case_sensitive=False,
                                                              metric=metric,
                                                              order="asc")
            self.assertTrue(len(model_list) > 0 and model_list[0]["model_id"] == self.model_id_2)
        except Exception as e:
            self.logger.error(f"test_find_and_rank_models_by_performance error: {e}")
            raise e
        self.assertRaises(expected_exception=Exception)

    def test_rank_models_by_performance(self):
        try:
            # See metrics in the config/global.json file.
            ranked_models = self.generators.rank_models_by_performance(
                model_ids=[self.model_id_1, self.model_id_2], metric="downstream_task.CLF.trained_on_real_and_fake.f1",
                order="desc")
            self.assertTrue(len(ranked_models) > 0 and ranked_models[0]["model_id"] == self.model_id_2)
        except Exception as e:
            self.logger.error(f"test_rank_models_by_performance error: {e}")
            raise e
        try:
            # See metrics in the config/global.json file.
            ranked_models_2 = self.generators.rank_models_by_performance(
                model_ids=[self.model_id_1, self.model_id_2], metric="turing_test.AUC",
                order="desc")
            self.assertTrue(len(ranked_models_2) > 0 and ranked_models_2[0]["model_id"] == self.model_id_2)
        except Exception as e:
            self.logger.error(f"test_rank_models_by_performance error: {e}")
            raise e
        self.assertRaises(expected_exception=Exception)

    def test_get_models_by_key_value_pair(self):
        try:
            key1 = "modality"
            value1 = "Full-Field Mammography"
            found_models = self.generators.get_models_by_key_value_pair(key1=key1, value1=value1,
                                                                        is_case_sensitive=False)
            self.assertTrue(len(found_models) > 2)

            key1 = "license"
            value1 = "BSD-3"
            found_models = self.generators.get_models_by_key_value_pair(key1=key1, value1=value1,
                                                                        is_case_sensitive=True)
            self.assertTrue(len(found_models) > 1)

            key1 = "performance.downstream_task.CLF.trained_on_real_and_fake.f1"
            value1 = 0.89
            found_models = self.generators.get_models_by_key_value_pair(key1=key1, value1=value1,
                                                                        is_case_sensitive=True)
            self.assertTrue(len(found_models) > 0)

            key1 = "performance.turing_test.AUC"
            value1 = 0.56
            found_models = self.generators.get_models_by_key_value_pair(key1=key1, value1=value1,
                                                                        is_case_sensitive=True)
            self.assertTrue(len(found_models) > 0)

        except Exception as e:
            self.logger.error(f"test_get_models_by_key_value_pair error: {e}")
            raise e
        self.assertRaises(expected_exception=Exception)

    def _check_if_samples_were_generated(self, models=[1, 2], num_samples=None,
                                         should_sample_be_generated: bool = True):
        if should_sample_be_generated:
            if 1 in models:
                # check if the number of generated samples of model_id_1 is as expected.
                file_list_1 = glob.glob(self.test_output_path1 + "/*")
                self.logger.debug(f"{len(file_list_1)} == {self.num_samples} ?")
                if num_samples is None:
                    self.assertTrue(len(file_list_1) == self.num_samples)
                else:
                    self.assertTrue(len(file_list_1) == num_samples)
            if 2 in models:
                # check if the number of generated samples of model_id_2 is as expected.
                file_list_2 = glob.glob(self.test_output_path2 + "/*")
                self.logger.debug(f"{len(file_list_2)} == {self.num_samples} ?")
                if num_samples is None:
                    self.assertTrue(len(file_list_2) == self.num_samples)
                else:
                    self.assertTrue(len(file_list_2) == num_samples)
            if 3 in models:
                # check if the number of generated samples of model_id_3 is as expected.
                file_list_3 = glob.glob(self.test_output_path3 + "/*")
                self.logger.debug(f"{len(file_list_3)} == {self.num_samples} ?")
                if num_samples is None:
                    self.assertTrue(len(file_list_3) == self.num_samples)
                else:
                    self.assertTrue(len(file_list_3) == num_samples)
        else:
            if 1 in models:
                # check if the sample have NOT been generated for model_id 1 and 2 and 3
                file_list_1 = glob.glob(self.test_output_path1 + "/*")
                self.logger.debug(f"{len(file_list_1)} != {self.num_samples}  ?")

                if num_samples is None:
                    self.assertTrue(len(file_list_1) != self.num_samples)
                else:
                    self.assertTrue(len(file_list_1) != num_samples)
            if 2 in models:
                file_list_2 = glob.glob(self.test_output_path2 + "/*")
                self.logger.debug(f"{len(file_list_2)} != {self.num_samples} ?")
                if num_samples is None:
                    self.assertTrue(len(file_list_2) != self.num_samples)
                else:
                    self.assertTrue(len(file_list_2) != num_samples)
            if 3 in models:
                file_list_3 = glob.glob(self.test_output_path3 + "/*")
                self.logger.debug(f"{len(file_list_3)} != {self.num_samples} ?")
                if num_samples is None:
                    self.assertTrue(len(file_list_3) != self.num_samples)
                else:
                    self.assertTrue(len(file_list_3) != num_samples)

    def _remove_dir_and_contents(self):
        # After each test, empty the created folders and files to avoid corrupting a new test.
        try:
            shutil.rmtree(self.test_output_path1)
            shutil.rmtree(self.test_output_path2)
            shutil.rmtree(self.test_output_path3)
        except OSError as e:
            # This may give an error if the folders are not created.
            self.logger.debug(
                f"Exception while trying to delete folder. Likely it simply had not yet been created: {e}")
        except Exception as e2:
            self.logger.error(f"Error while trying to delete folder: {e2}")


if __name__ == '__main__':
    unittest.main()
