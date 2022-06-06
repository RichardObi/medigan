# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" script for quick local testing if new models work inside medigan.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
"""
# run with python -m tests.model_contribution_test_manual

import glob
import logging
import shutil
import sys
import unittest

try:
    from src.medigan.generators import Generators

    LOGGING_LEVEL = 'INFO'
    logger = logging.getLogger()  # (__name__)
    logger.setLevel(LOGGING_LEVEL)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(LOGGING_LEVEL)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    generators = Generators()

    # Testing init of contributor with erroneous params
    # contributor = generators.add_model_contributor(model_id ='Some model id', init_py_path="somePath")
    # contributor = generators.add_model_contributor(model_id ='00008_WGANGP_MMG_MASS_ROI', init_py_path="somePath")
    # contributor = generators.add_model_contributor(model_id ='Some model id', init_py_path="/Users/richardosuala/Desktop/00008_WGANGP_MMG_MASS_ROI")

    # Testing init of contributor with correct params
    init_py_path = "/Users/richardosuala/Desktop/00008_WGANGP_MMG_MASS_ROI/__init__.py"
    model_id = '00008_WGANGP_MMG_MASS_ROI'
    contributor = generators.add_model_contributor(model_id=model_id, init_py_path=init_py_path)

    # Adding the metadata of the model from file
    # metadata = contributor.add_metadata_from_input(
    #                                               model_weights_name = "10000",
    #                                               model_weights_extension=".pt",
    #                                               generate_method_name = "generate",
    #                                               dependencies=["numpy", "torch", "opencv-contrib-python-headless"])

    # Adding the metadata of the model from input
    metadata_file_path = "/Users/richardosuala/Desktop/00008_WGANGP_MMG_MASS_ROI/metadata.json"
    metadata = contributor.add_metadata_from_file(metadata_file_path=metadata_file_path)
    generators.add_model_to_config(model_id=model_id, metadata=metadata, metadata_file_path=metadata_file_path,
                                   overwrite_existing_metadata=True)


except Exception as e:
    logging.error(f"test_init_generators error: {e}")
    raise e
