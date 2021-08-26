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
        self.num_samples1 = 3
        self.num_samples2 = 3
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
            self.generators.generate(model_id=self.model_id_1, num_samples=self.num_samples1,
                                     output_path=self.test_output_path1)

            self.generators.generate(model_id=self.model_id_2, num_samples=self.num_samples2,
                                     output_path=self.test_output_path2)

        except Exception as e:
            self.logger.error(f"test_generate_methods error: {e}")
            raise e
        self.assertRaises(expected_exception=Exception)

        # check if the number of generated files of model_id_1 is as expected.
        file_list_1 = glob.glob(self.test_output_path1 + "/*")
        self.logger.info(f"{len(file_list_1)} == {self.num_samples1}")
        self.assertTrue(len(file_list_1) == self.num_samples1)

        # check if the number of generated files of model_id_2 is as expected.
        file_list_2 = glob.glob(self.test_output_path2 + "/*")
        self.logger.debug(f"{len(file_list_2)} == {self.num_samples2}")
        self.assertTrue(len(file_list_2) == self.num_samples2)
        self.remove_dir_and_contents()

    def test_generate_methods_with_additional_args(self):
        # At the moment, no optional test_dict params are implemented in the model's generate methods.
        # TODO Add some valid key value pairs into test_dicts below and test.
        test_dict_1 = {}
        test_dict_2 = {}
        try:
            self.generators.generate(model_id=self.model_id_1, num_samples=self.num_samples1,
                                     output_path=self.test_output_path1, **test_dict_1)

            self.generators.generate(model_id=self.model_id_2, num_samples=self.num_samples2,
                                     output_path=self.test_output_path2, **test_dict_2)

        except Exception as e:
            self.logger.error(f"test_generate_methods_with_additional_args error: {e}")
            raise e
        self.assertRaises(expected_exception=Exception)

        # check if the number of generated files of model_id_1 is as expected.
        file_list_1 = glob.glob(self.test_output_path1 + "/*")
        self.logger.info(f"{len(file_list_1)} == {self.num_samples1}")
        self.assertTrue(len(file_list_1) == self.num_samples1)

        # check if the number of generated files of model_id_2 is as expected.
        file_list_2 = glob.glob(self.test_output_path2 + "/*")
        self.logger.debug(f"{len(file_list_2)} == {self.num_samples2}")
        self.assertTrue(len(file_list_2) == self.num_samples2)
        self.remove_dir_and_contents()

    def remove_dir_and_contents(self):
        # After each test, empty the created folders and files to avoid corrupting a new test.
        try:
            shutil.rmtree(self.test_output_path1)
            shutil.rmtree(self.test_output_path2)
        except OSError as e:
            self.logger.error("Error: %s - %s." % (e.filename, e.strerror))


if __name__ == '__main__':
    unittest.main()
