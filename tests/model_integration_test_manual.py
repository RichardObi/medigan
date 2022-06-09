# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" script for quick local testing if new models work inside medigan.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""
# run with python -m tests.model_integration_test_manual

import logging


MODEL_ID = "00007_BEZIERCURVE_TUMOUR_MASK" #"00002_DCGAN_MMG_MASS_ROI" #
#MODEL_ID = "YOUR_MODEL_ID_HERE"
NUM_SAMPLES = 10
IMAGE_SIZE = 55
OUTPUT_PATH = f"output/{MODEL_ID}/"
try:
    from src.medigan.generators import Generators

    generators = Generators()
except Exception as e:
    logging.error(f"test_init_generators error: {e}")
    raise e

generators.generate(
    model_id=MODEL_ID,
    num_samples=NUM_SAMPLES,
    output_path=OUTPUT_PATH,
    image_size=IMAGE_SIZE,
)
