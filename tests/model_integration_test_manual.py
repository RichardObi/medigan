# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" script for quick local testing if a model works inside medigan."""
# run with python -m tests.model_integration_test_manual

import logging

MODEL_ID = "YOUR_MODEL_ID_HERE"
MODEL_ID = 23 #"00023_PIX2PIXHD_BREAST_DCEMRI" #"00002_DCGAN_MMG_MASS_ROI"  # "00007_BEZIERCURVE_TUMOUR_MASK"
NUM_SAMPLES = 2
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
    input_path="input/",
    gpu_id= 0,
    image_size=448,
    install_dependencies=True,

)

data_loader = generators.get_as_torch_dataloader(
    model_id=MODEL_ID,
    num_samples=NUM_SAMPLES,
    output_path=OUTPUT_PATH,
    input_path="input/",
    gpu_id=0,
    image_size=448,
    # prefetch_factor=2, # debugging with torch v2.0.0: This will raise an error for torch DataLoader if num_workers == None at the same time.
)

print(f"len(data_loader): {len(data_loader)}")

if len(data_loader) != NUM_SAMPLES:
    logging.warning(
        f"{MODEL_ID}: The number of samples in the dataloader (={len(data_loader)}) is not equal the number of samples requested (={NUM_SAMPLES}).")

#### Get the object at index 0 from the dataloader
data_dict = next(iter(data_loader))

print(f"data_dict: {data_dict}")
