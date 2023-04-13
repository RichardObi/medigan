# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" script for quick local testing if a model works inside medigan."""
# run with python -m tests.model_integration_test_manual

import logging

MODEL_ID = "YOUR_MODEL_ID_HERE"
MODEL_ID = "00002_DCGAN_MMG_MASS_ROI" #"00007_BEZIERCURVE_TUMOUR_MASK"
NUM_SAMPLES = 10
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
)

generators.get_as_torch_dataloader(
    model_id=MODEL_ID,
    num_samples=NUM_SAMPLES,
    output_path=OUTPUT_PATH,
    #prefetch_factor=2, # debugging with torch v2.0.0: This will raise an error for torch DataLoader if num_workers == None at the same time.
)