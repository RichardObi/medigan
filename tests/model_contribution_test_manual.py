# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" script for quick local testing if a new model can be added and works inside medigan."""
# run with python -m tests.model_contribution_test_manual

import glob
import logging
import shutil
import sys
import unittest

try:
    from src.medigan.generators import Generators

    LOGGING_LEVEL = "INFO"
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

    # Testing init of contributor with correct params
    init_py_path = "models/00012_C-DCGAN_MMG_MASSES/__init__.py"
    metadata_file_path = "models/00012_C-DCGAN_MMG_MASSES/metadata.json"
    model_id = "00012_C-DCGAN_MMG_MASSES"

    zenodo_access_token = "ACCESS_TOKEN"
    github_access_token = "ACCESS_TOKEN"

    creator_name = "John Doe"
    creator_affiliation = "University of Barcelona"

    # Testing full model contribution workflow.
    generators.contribute(
        model_id=model_id,
        init_py_path=init_py_path,
        zenodo_access_token=zenodo_access_token,
        github_access_token=github_access_token,
        metadata_file_path=metadata_file_path,
        creator_name=creator_name,
        creator_affiliation=creator_affiliation,
    )

    # Testing init of contributor with erroneous params
    # contributor = generators.add_model_contributor(model_id ='Some model id', init_py_path="somePath")
    # contributor = generators.add_model_contributor(model_id ='00008_WGANGP_MMG_MASS_ROI', init_py_path="somePath")
    # contributor = generators.add_model_contributor(model_id ='Some model id', init_py_path="init_py_path")

    # Creating the model contributor
    # generators.add_model_contributor(model_id=model_id, init_py_path=init_py_path)

    # Adding the metadata of the model from input
    # generators.add_metadata_from_file(
    #    model_id=model_id, metadata_file_path=metadata_file_path
    # )

    #  Alternatively, Adding the metadata of the model from file
    # metadata = contributor.add_metadata_from_input(
    #                                               model_weights_name = "10000",
    #                                               model_weights_extension=".pt",
    #                                               generate_method_name = "generate",
    #                                               dependencies=["numpy", "torch", "opencv-contrib-python-headless"])

    # Add metadata to global.json config
    # generators.test_model(model_id=model_id)

    # Alternatively, explicitely providing model metadata to add the metadata to config
    # generators._add_model_to_config(model_id=model_id, metadata=metadata, metadata_file_path=metadata_file_path,
    #                               overwrite_existing_metadata=True)

    # Zenodo upload test
    # generators.push_to_zenodo(
    #    model_id=model_id,
    #    access_token=zenodo_access_token,
    #    creator_name="test",
    #    creator_affiliation="test affiliation",
    # )

    # Manual Zenodo Test 1
    # import requests
    # r = requests.get('https://zenodo.org/api/deposit/depositions', params = {'access_token': zenodo_access_token})
    # print(r.status_code)
    # print(r.json())

    # Manual Zenodo Test 2
    # headers = {"Content-Type": "application/json"}
    # params = {"access_token": zenodo_access_token}
    # r = requests.post(
    #    "https://zenodo.org/api/deposit/depositions",
    #    params=params,
    #    json={},
    #    headers=headers,
    # )
    # print(r.json())
    # print(r.status_code)

    # Github upload test
    # generators.push_to_github(
    #    model_id=model_id,
    #    github_access_token=github_access_token,
    #    package_link=None,
    #    creator_name="test",
    #    creator_affiliation="test affiliation",
    #    model_description="test description",
    # )

except Exception as e:
    logging.error(f"test_init_generators error: {e}")
    raise e
