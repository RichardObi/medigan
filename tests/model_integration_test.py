# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" script for quick local testing if new models work inside medigan.
.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""
# run with python -m tests.model_integration_test


import logging
import unittest


class MyTestCase(unittest.TestCase):
    def test_local_model(self):

        MODEL_ID = "YOUR_MODEL_ID_HERE"
        NUM_SAMPLES = 10
        OUTPUT_PATH = f"output/{MODEL_ID}/"

        try:
            from src.medigan.generators import Generators
            generators = Generators()
            generators.generate(model_id=MODEL_ID, num_samples=NUM_SAMPLES, output_path=OUTPUT_PATH)

        except Exception as e:
            logging.error(f"test_init_generators error: {e}")
            raise e
        self.assertRaises(Exception)

if __name__ == '__main__':
    unittest.main()
